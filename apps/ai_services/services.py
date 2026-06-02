import hashlib
import json
import logging

from django.conf import settings
from django.db.models import Q

from apps.ai_services.models import AIInteractionLog
from apps.recipes.models import Recipe
from apps.users.models import Profile

logger = logging.getLogger(__name__)


class OpenAIRecommendationService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-5.2')

    def eligible_recipes(self, profile, household=None):
        allergies = {item.lower() for item in profile.allergies}
        dislikes = {item.lower() for item in profile.dislikes}
        query = Q(is_public=True)
        if household:
            query |= Q(household=household)
        recipes = Recipe.objects.filter(query).distinct().prefetch_related('ingredients__ingredient')
        eligible = []
        for recipe in recipes:
            haystack = ' '.join(
                [recipe.title, recipe.description, recipe.diet_type, ' '.join(recipe.allergens), ' '.join(recipe.tags)]
                + [item.ingredient.name for item in recipe.ingredients.all()]
            ).lower()
            if any(allergy in haystack for allergy in allergies):
                continue
            if any(dislike in haystack for dislike in dislikes):
                continue
            if profile.diet_type not in ('none', recipe.diet_type) and recipe.diet_type != 'none':
                continue
            eligible.append(recipe)
        return eligible

    def rank_recipes(self, user, limit=5):
        profile, _ = Profile.objects.get_or_create(user=user)
        candidates = self.eligible_recipes(profile, user.active_household)
        if not candidates:
            return []

        if not self.api_key:
            # The local fallback keeps the app useful when no OpenAI key is configured.
            ranked = self._fallback_rank(profile, candidates, limit)
            self._log(user, 'recipe_recommendations', AIInteractionLog.Status.FALLBACK, ranked)
            return ranked

        payload = {
            'profile': profile.preference_summary(),
            'recipes': [
                {
                    'id': recipe.id,
                    'title': recipe.title,
                    'diet_type': recipe.diet_type,
                    'tags': recipe.tags,
                    'cost_xaf': float(recipe.estimated_cost_xaf),
                    'calories': recipe.calories,
                }
                for recipe in candidates[:30]
            ],
        }
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.responses.create(
                model=self.model,
                input=[
                    {
                        'role': 'system',
                        'content': 'Rank recipes for a meal planner. Never recommend recipes that violate allergies or stated dislikes.',
                    },
                    {
                        'role': 'user',
                        'content': json.dumps(payload),
                    },
                ],
                text={
                    'format': {
                        'type': 'json_schema',
                        'name': 'recipe_rankings',
                        'schema': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {
                                'rankings': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'additionalProperties': False,
                                        'properties': {
                                            'recipe_id': {'type': 'integer'},
                                            'score': {'type': 'number'},
                                            'reason': {'type': 'string'},
                                        },
                                        'required': ['recipe_id', 'score', 'reason'],
                                    },
                                },
                            },
                            'required': ['rankings'],
                        },
                    },
                },
            )
            data = json.loads(response.output_text)
            ranked = self._hydrate_rankings(candidates, data.get('rankings', []), limit)
            self._log(user, 'recipe_recommendations', AIInteractionLog.Status.SUCCESS, ranked)
            return ranked
        except Exception as exc:
            logger.warning("OpenAI recommendation fallback used: %s", exc)
            ranked = self._fallback_rank(profile, candidates, limit)
            self._log(user, 'recipe_recommendations', AIInteractionLog.Status.ERROR, ranked, {'error': str(exc)[:180]})
            return ranked

    def _fallback_rank(self, profile, candidates, limit):
        likes = {item.lower() for item in profile.likes}
        ranked = []
        for recipe in candidates:
            text = ' '.join([recipe.title, recipe.description, ' '.join(recipe.tags)]).lower()
            score = 0.5
            score += sum(0.1 for like in likes if like in text)
            score -= min(float(recipe.estimated_cost_xaf) / max(profile.weekly_budget_xaf, 1), 0.3)
            ranked.append({'recipe': recipe, 'score': round(score, 2), 'reason': 'Matched locally using your profile and budget.'})
        ranked.sort(key=lambda item: item['score'], reverse=True)
        return ranked[:limit]

    def _hydrate_rankings(self, candidates, rankings, limit):
        by_id = {recipe.id: recipe for recipe in candidates}
        hydrated = []
        for item in rankings:
            recipe = by_id.get(item.get('recipe_id'))
            if recipe:
                score = item.get('score', 0)
                try:
                    score = max(0, min(float(score), 1))
                except (TypeError, ValueError):
                    score = 0
                hydrated.append(
                    {
                        'recipe': recipe,
                        'score': score,
                        'reason': self._clip(item.get('reason') or 'AI suggested', 240),
                    }
                )
        return hydrated[:limit]

    def _clip(self, value, limit):
        return str(value).strip()[:limit]

    def _log(self, user, operation, status, ranked, metadata=None):
        # Store a hash and summary, not raw prompts or model responses.
        compact = [{'recipe_id': item['recipe'].id, 'score': item['score']} for item in ranked]
        input_hash = hashlib.sha256(json.dumps(compact, sort_keys=True).encode()).hexdigest()
        AIInteractionLog.objects.create(
            user=user,
            operation=operation,
            provider='openai',
            model=self.model if self.api_key else 'local-fallback',
            status=status,
            input_hash=input_hash,
            output_summary=f"{len(ranked)} recipes ranked",
            metadata=metadata or {},
        )

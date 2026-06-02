import hashlib
import json
import logging
import math
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from apps.ai_services.models import AIInteractionLog
from apps.recipes.models import Ingredient

from .models import MealAnalysis, MealIngredient

logger = logging.getLogger(__name__)


class MealIngredientService:
    MAX_ROWS = 25
    MAX_QUANTITY = 100000
    MAX_UNIT_PRICE = Decimal('10000000')

    @staticmethod
    @transaction.atomic
    def sync_from_form(meal, ingredient_rows):
        # Replace the custom ingredient rows with the latest submitted form rows.
        meal.custom_ingredients.all().delete()
        created = []
        for row in ingredient_rows[:MealIngredientService.MAX_ROWS]:
            name = (row.get('name') or '').strip()[:255]
            if not name:
                continue
            ingredient = None
            ingredient_id = row.get('ingredient_id')
            if ingredient_id:
                ingredient = Ingredient.objects.filter(pk=ingredient_id).first()
            if ingredient is None:
                ingredient = Ingredient.objects.filter(name__iexact=name).first()

            quantity = MealIngredientService._bounded_float(row.get('quantity'), 0, MealIngredientService.MAX_QUANTITY)
            unit = ((row.get('unit') or (ingredient.default_unit if ingredient else 'g')).strip() or 'g')[:50]
            unit_price = MealIngredientService._decimal_or_none(row.get('unit_price_xaf'))
            if unit_price is not None:
                unit_price = max(Decimal('0'), min(unit_price, MealIngredientService.MAX_UNIT_PRICE))
            created.append(
                MealIngredient.objects.create(
                    meal=meal,
                    ingredient=ingredient,
                    name=ingredient.name if ingredient else name,
                    quantity=quantity,
                    unit=unit,
                    unit_price_xaf=unit_price,
                )
            )
        return created

    @staticmethod
    def parse_rows(post_data):
        # Dynamic HTML inputs use [] names; getlist reads every repeated value.
        names = post_data.getlist('ingredient_name[]')
        quantities = post_data.getlist('ingredient_quantity[]')
        units = post_data.getlist('ingredient_unit[]')
        prices = post_data.getlist('ingredient_unit_price_xaf[]')
        ids = post_data.getlist('ingredient_id[]')
        rows = []
        for index, name in enumerate(names[:MealIngredientService.MAX_ROWS]):
            rows.append(
                {
                    'name': name,
                    'quantity': quantities[index] if index < len(quantities) else '',
                    'unit': units[index] if index < len(units) else '',
                    'unit_price_xaf': prices[index] if index < len(prices) else '',
                    'ingredient_id': ids[index] if index < len(ids) else '',
                }
            )
        return rows

    @staticmethod
    def _float(value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _bounded_float(value, default, maximum):
        return max(0, min(MealIngredientService._float(value, default), maximum))

    @staticmethod
    def _decimal_or_none(value):
        if value in (None, ''):
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None


class MealCostService:
    @staticmethod
    def calculate(meal):
        if meal.entry_type == 'recipe' and meal.recipe:
            multiplier = meal.servings / max(meal.recipe.servings, 1)
            return Decimal(str(meal.recipe.estimated_cost_xaf)) * Decimal(str(multiplier))
        return sum((item.total_price_xaf for item in meal.custom_ingredients.all()), Decimal('0'))


class MealAnalysisService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-5.2')

    def analyze(self, meal):
        # Prefer exact local data. Use OpenAI only when custom ingredients are unknown.
        if meal.entry_type == 'recipe' and meal.recipe:
            payload = self._recipe_payload(meal)
            return self._save(meal, payload, MealAnalysis.Status.LOCAL, 'local', is_estimated=False)

        local_payload, has_unknown = self._custom_local_payload(meal)
        if not has_unknown:
            return self._save(meal, local_payload, MealAnalysis.Status.LOCAL, 'local', is_estimated=False)

        if self.api_key:
            try:
                ai_payload = self._openai_payload(meal, local_payload)
                analysis = self._save(meal, ai_payload, MealAnalysis.Status.AI, 'openai', is_estimated=True)
                self._log(meal, AIInteractionLog.Status.SUCCESS, analysis)
                return analysis
            except Exception as exc:
                logger.warning("OpenAI meal analysis fallback used: %s", exc)
                local_payload['limitations'].append('OpenAI analysis was unavailable, so EatFit used local estimates.')

        analysis = self._save(meal, local_payload, MealAnalysis.Status.FALLBACK, 'local-fallback', is_estimated=True)
        self._log(meal, AIInteractionLog.Status.FALLBACK, analysis)
        return analysis

    def _recipe_payload(self, meal):
        recipe = meal.recipe
        multiplier = meal.servings / max(recipe.servings, 1)
        calories = recipe.calories * multiplier
        protein = recipe.protein * multiplier
        carbs = recipe.carbs * multiplier
        fat = recipe.fat * multiplier
        return self._build_payload(
            calories,
            protein,
            carbs,
            fat,
            MealCostService.calculate(meal),
            [
                'Uses a structured recipe with known ingredient nutrition.',
                'Provides predictable cost and macro estimates.',
            ],
            self._risks_for(calories, protein, carbs, fat),
            'Analysis is calculated from saved recipe nutrition values.',
            ['Nutrition values are estimates and not medical advice.'],
            0.85,
        )

    def _custom_local_payload(self, meal):
        calories = protein = carbs = fat = 0
        unknown = []
        for item in meal.custom_ingredients.select_related('ingredient'):
            ingredient = item.ingredient
            if ingredient is None:
                unknown.append(item.name)
                calories += item.quantity * 1.2
                carbs += item.quantity * 0.2
                protein += item.quantity * 0.03
                fat += item.quantity * 0.02
                continue
            calories += ingredient.calories_per_unit * item.quantity
            protein += ingredient.protein_per_unit * item.quantity
            carbs += ingredient.carbs_per_unit * item.quantity
            fat += ingredient.fat_per_unit * item.quantity

        benefits = ['Accepts your own meal and ingredient choices.']
        if protein >= 25:
            benefits.append('Good protein contribution for fullness and muscle maintenance.')
        if carbs >= 50:
            benefits.append('Provides energy from carbohydrate-rich ingredients.')
        if meal.custom_ingredients.count() >= 3:
            benefits.append('Multiple ingredients can improve meal variety.')

        limitations = ['Nutrition values are estimates and not medical advice.']
        if unknown:
            limitations.append(f"Unknown ingredients estimated locally: {', '.join(unknown[:5])}.")

        return (
            self._build_payload(
                calories,
                protein,
                carbs,
                fat,
                MealCostService.calculate(meal),
                benefits,
                self._risks_for(calories, protein, carbs, fat),
                'EatFit analyzed the custom meal from entered ingredients and available local nutrition data.',
                limitations,
                0.55 if unknown else 0.8,
            ),
            bool(unknown),
        )

    def _openai_payload(self, meal, local_payload):
        from openai import OpenAI

        ingredients = [
            {
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'has_local_nutrition': bool(item.ingredient_id),
                'price_xaf': float(item.total_price_xaf),
            }
            for item in meal.custom_ingredients.all()
        ]
        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input=[
                {
                    'role': 'system',
                    'content': (
                        'Analyze a meal for general nutrition education only. '
                        'Do not give medical advice, diagnoses, or treatment instructions. '
                        'Return concise, practical benefits and risks.'
                    ),
                },
                {
                    'role': 'user',
                    'content': json.dumps(
                        {
                            'meal_title': meal.recipe_name,
                            'servings': meal.servings,
                            'ingredients': ingredients,
                            'local_estimate': {
                                **local_payload,
                                'estimated_total_cost_xaf': float(local_payload.get('estimated_total_cost_xaf', 0)),
                            },
                        }
                    ),
                },
            ],
            text={
                'format': {
                    'type': 'json_schema',
                    'name': 'meal_analysis',
                    'schema': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'summary': {'type': 'string'},
                            'benefits': {'type': 'array', 'items': {'type': 'string'}},
                            'risks': {'type': 'array', 'items': {'type': 'string'}},
                            'nutrition_strength': {'type': 'string'},
                            'calories': {'type': 'number'},
                            'protein': {'type': 'number'},
                            'carbs': {'type': 'number'},
                            'fat': {'type': 'number'},
                            'confidence': {'type': 'number'},
                            'limitations': {'type': 'array', 'items': {'type': 'string'}},
                        },
                        'required': [
                            'summary',
                            'benefits',
                            'risks',
                            'nutrition_strength',
                            'calories',
                            'protein',
                            'carbs',
                            'fat',
                            'confidence',
                            'limitations',
                        ],
                    },
                },
            },
        )
        data = json.loads(response.output_text)
        return self._build_payload(
            data['calories'],
            data['protein'],
            data['carbs'],
            data['fat'],
            MealCostService.calculate(meal),
            data['benefits'],
            data['risks'],
            data['summary'],
            data['limitations'] + ['AI estimates are advisory and not medical advice.'],
            data['confidence'],
            data['nutrition_strength'],
        )

    def _build_payload(self, calories, protein, carbs, fat, cost, benefits, risks, summary, limitations, confidence, strength=None):
        calories = self._finite_float(calories)
        protein = self._finite_float(protein)
        carbs = self._finite_float(carbs)
        fat = self._finite_float(fat)
        score = self._score(calories, protein, carbs, fat)
        return {
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fat': fat,
            'estimated_total_cost_xaf': Decimal(str(cost or 0)).quantize(Decimal('0.01')),
            'nutrition_strength_score': score,
            'nutrition_strength': self._clip(strength or self._strength_label(score, protein, carbs, fat), 80),
            'health_benefits': self._clip_list(benefits, 6, 240),
            'health_risks': self._clip_list(risks, 6, 240),
            'advisory_summary': self._clip(summary, 1000),
            'limitations': self._clip_list(limitations, 6, 240),
            'confidence': max(0, min(self._finite_float(confidence), 1)),
        }

    def _finite_float(self, value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0
        if not math.isfinite(number):
            return 0
        return round(number, 1)

    def _clip(self, value, limit):
        return str(value or '').strip()[:limit]

    def _clip_list(self, values, item_limit, char_limit):
        if not isinstance(values, list):
            return []
        return [self._clip(value, char_limit) for value in values[:item_limit] if self._clip(value, char_limit)]

    def _save(self, meal, payload, status, provider, is_estimated):
        # update_or_create lets a meal be re-analyzed without making duplicate rows.
        analysis, _ = MealAnalysis.objects.update_or_create(
            meal=meal,
            defaults={
                **payload,
                'status': status,
                'provider': provider,
                'is_estimated': is_estimated,
                'metadata': {'advisory': True},
            },
        )
        return analysis

    def _risks_for(self, calories, protein, carbs, fat):
        risks = ['Review portion size and personal health needs before relying on this analysis.']
        if calories > 900:
            risks.append('High energy meal; may exceed calorie goals depending on the rest of the day.')
        if fat > 45:
            risks.append('Fat estimate is high; consider balancing oil-rich ingredients.')
        if protein < 10:
            risks.append('Protein appears low; consider adding a protein source if appropriate.')
        return risks

    def _score(self, calories, protein, carbs, fat):
        score = 50
        if 350 <= calories <= 800:
            score += 15
        if protein >= 20:
            score += 15
        if 30 <= carbs <= 120:
            score += 10
        if fat <= 35:
            score += 10
        return min(score, 100)

    def _strength_label(self, score, protein, carbs, fat):
        if score >= 80 and protein >= 20:
            return 'Balanced'
        if protein >= 35:
            return 'Protein rich'
        if carbs >= 100:
            return 'High energy'
        return 'Needs review'

    def _log(self, meal, status, analysis):
        if not meal.meal_plan.created_by_id:
            return
        compact = {
            'meal_id': meal.id,
            'ingredient_count': meal.custom_ingredients.count(),
            'analysis_id': analysis.id,
            'status': analysis.status,
        }
        input_hash = hashlib.sha256(json.dumps(compact, sort_keys=True).encode()).hexdigest()
        AIInteractionLog.objects.create(
            user=meal.meal_plan.created_by,
            operation='meal_analysis',
            provider='openai' if status == AIInteractionLog.Status.SUCCESS else 'local-fallback',
            model=self.model if status == AIInteractionLog.Status.SUCCESS else 'local-fallback',
            status=status,
            input_hash=input_hash,
            output_summary=f"Analyzed meal {meal.id}",
            metadata={'meal_id': meal.id, 'analysis_id': analysis.id},
        )

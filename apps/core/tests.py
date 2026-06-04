from datetime import date, timedelta

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.ai_services.models import AIInteractionLog
from apps.ai_services.services import OpenAIRecommendationService
from apps.groceries.services import GroceryGenerationService
from apps.meals.models import Meal, MealAnalysis, MealIngredient, MealPlan
from apps.meals.services import MealAnalysisService, MealCostService
from apps.notifications.models import Notification
from apps.notifications.services import ReminderService
from apps.recipes.models import Ingredient, Recipe, RecipeIngredient
from apps.users.session_lifecycle import (
    SESSION_LAST_SEEN_AT,
    SESSION_REMEMBERED,
    SESSION_ROTATED_AT,
    SESSION_STARTED_AT,
    SESSION_USER_AGENT_HASH,
    _now,
    _stable_hash,
)
from apps.users.models import HouseholdMembership, Profile, User


@override_settings(SECURE_SSL_REDIRECT=False, OPENAI_API_KEY='')
class EatFitFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='nurdi', email='nurdi@example.com', password='StrongPass123!')
        self.household = self.user.ensure_household()
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.profile.weekly_budget_xaf = 5000
        self.profile.save()
        self.ingredient = Ingredient.objects.create(
            name='Plantain',
            category='produce',
            default_unit='g',
            estimated_cost_per_unit_xaf=2,
            calories_per_unit=1,
            carbs_per_unit=0.3,
        )
        self.recipe = Recipe.objects.create(
            title='Boiled Plantain',
            description='Simple plantain meal',
            instructions='Boil plantains until tender.',
            prep_time=5,
            cook_time=20,
            servings=2,
            household=self.household,
            created_by=self.user,
            is_public=False,
        )
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.ingredient, quantity=400, unit='g')
        self.plan = MealPlan.objects.create(
            household=self.household,
            title='Test Week',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=6),
            created_by=self.user,
        )
        self.meal = Meal.objects.create(
            meal_plan=self.plan,
            recipe=self.recipe,
            recipe_name=self.recipe.title,
            date=date.today(),
            meal_type='breakfast',
            servings=2,
        )

    def _prepare_authenticated_session(self, user_agent='EatFitTestBrowser/1'):
        self.client.force_login(self.user)
        session = self.client.session
        now = _now()
        session[SESSION_STARTED_AT] = now
        session[SESSION_LAST_SEEN_AT] = now
        session[SESSION_ROTATED_AT] = now
        session[SESSION_REMEMBERED] = False
        session[SESSION_USER_AGENT_HASH] = _stable_hash(user_agent)
        session.save()
        return session

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_registration_creates_household_profile_and_session(self):
        client = Client()
        response = client.post(
            reverse('auth:register'),
            {
                'username': 'deirdre',
                'email': 'deirdre@example.com',
                'first_name': 'Deirdre',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='deirdre')
        self.assertIsNotNone(user.active_household)
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertIn(SESSION_STARTED_AT, client.session)
        self.assertFalse(client.session.get(SESSION_REMEMBERED))

    def test_login_initializes_session_lifecycle(self):
        response = self.client.post(
            reverse('auth:login'),
            {'username': 'nurdi', 'password': 'StrongPass123!'},
            HTTP_USER_AGENT='EatFitTestBrowser/1',
        )
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertIn(SESSION_STARTED_AT, session)
        self.assertIn(SESSION_LAST_SEEN_AT, session)
        self.assertIn(SESSION_ROTATED_AT, session)
        self.assertFalse(session.get(SESSION_REMEMBERED))

    def test_remember_me_uses_persistent_session_window(self):
        response = self.client.post(
            reverse('auth:login'),
            {'username': 'nurdi', 'password': 'StrongPass123!', 'remember-me': 'on'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get(SESSION_REMEMBERED))
        self.assertGreaterEqual(self.client.session.get_expiry_age(), 60 * 60 * 24 * 6)

    @override_settings(SESSION_IDLE_TIMEOUT_SECONDS=60)
    def test_idle_timeout_terminates_authenticated_session(self):
        session = self._prepare_authenticated_session()
        session[SESSION_LAST_SEEN_AT] = _now() - 120
        session.save()

        response = self.client.get(reverse('dashboard'), HTTP_USER_AGENT='EatFitTestBrowser/1')
        self.assertEqual(response.status_code, 302)
        self.assertIn('session=idle_timeout', response.url)
        self.assertEqual(response['Clear-Site-Data'], '"cookies", "storage"')
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(SESSION_ABSOLUTE_TIMEOUT_SECONDS=60)
    def test_absolute_timeout_terminates_authenticated_session(self):
        session = self._prepare_authenticated_session()
        session[SESSION_STARTED_AT] = _now() - 120
        session.save()

        response = self.client.get(reverse('dashboard'), HTTP_USER_AGENT='EatFitTestBrowser/1')
        self.assertEqual(response.status_code, 302)
        self.assertIn('session=absolute_timeout', response.url)
        self.assertEqual(response['Clear-Site-Data'], '"cookies", "storage"')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_user_agent_change_terminates_authenticated_session(self):
        self._prepare_authenticated_session(user_agent='EatFitTestBrowser/1')
        response = self.client.get(reverse('dashboard'), HTTP_USER_AGENT='DifferentBrowser/2')
        self.assertEqual(response.status_code, 302)
        self.assertIn('session=client_changed', response.url)
        self.assertEqual(response['Clear-Site-Data'], '"cookies", "storage"')
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(SESSION_ROTATION_SECONDS=60)
    def test_session_key_rotates_during_long_lived_session(self):
        self._prepare_authenticated_session()
        old_session_key = self.client.session.session_key
        session = self.client.session
        session[SESSION_ROTATED_AT] = _now() - 120
        session.save()

        response = self.client.get(reverse('dashboard'), HTTP_USER_AGENT='EatFitTestBrowser/1')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(old_session_key, self.client.session.session_key)

    def test_logout_flushes_session_and_sets_cleanup_headers(self):
        self._prepare_authenticated_session()
        response = self.client.post(reverse('auth:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Clear-Site-Data'], '"cookies", "storage"')
        self.assertEqual(response['Cache-Control'], 'no-store, private')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_grocery_generation_merges_structured_ingredients(self):
        grocery_list = GroceryGenerationService.generate(self.plan, self.user)
        self.assertEqual(grocery_list.items.count(), 1)
        item = grocery_list.items.get()
        self.assertEqual(item.quantity, 400)
        self.assertEqual(float(grocery_list.total_estimated_cost_xaf), 800.0)

    def test_cross_household_meal_plan_is_not_visible(self):
        other = User.objects.create_user(username='other', password='StrongPass123!')
        other.ensure_household()
        self.client.force_login(other)
        response = self.client.get(reverse('meals:detail', args=[self.plan.pk]))
        self.assertEqual(response.status_code, 404)

    def test_reminder_service_creates_in_app_notification(self):
        created = ReminderService.schedule(self.meal)
        self.assertEqual(len(created), 1)
        self.assertTrue(Notification.objects.filter(user=self.user, notification_type='meal_reminder').exists())

    @override_settings(OPENAI_API_KEY='')
    def test_ai_fallback_does_not_store_raw_prompt(self):
        ranked = OpenAIRecommendationService().rank_recipes(self.user)
        self.assertTrue(ranked)
        log = AIInteractionLog.objects.get(user=self.user)
        self.assertEqual(log.status, AIInteractionLog.Status.FALLBACK)
        self.assertFalse(hasattr(log, 'prompt'))
        self.assertFalse(hasattr(log, 'response'))

    def test_family_role_membership_exists_for_owner(self):
        membership = HouseholdMembership.objects.get(user=self.user, household=self.household)
        self.assertEqual(membership.role, HouseholdMembership.Role.OWNER)

    def test_core_pages_render_for_authenticated_user(self):
        self.client.force_login(self.user)
        urls = [
            reverse('dashboard'),
            reverse('recipes:index'),
            reverse('meals:index'),
            reverse('meals:detail', args=[self.plan.pk]),
            reverse('groceries:index'),
            reverse('pantry:index'),
            reverse('nutrition:index'),
            reverse('budget'),
            reverse('notifications:index'),
            reverse('profile'),
            reverse('households'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_custom_meal_can_store_free_text_ingredients_and_prices(self):
        meal = Meal.objects.create(
            meal_plan=self.plan,
            entry_type='custom',
            recipe_name='Fried plantain and eggs',
            date=date.today() + timedelta(days=1),
            meal_type='lunch',
            servings=1,
        )
        ingredient = MealIngredient.objects.create(
            meal=meal,
            name='Eggs',
            quantity=3,
            unit='pcs',
            unit_price_xaf=150,
        )
        self.assertIsNone(meal.recipe)
        self.assertEqual(float(ingredient.total_price_xaf), 450.0)
        self.assertEqual(float(MealCostService.calculate(meal)), 450.0)

    def test_known_custom_ingredient_gets_local_analysis(self):
        meal = Meal.objects.create(
            meal_plan=self.plan,
            entry_type='custom',
            recipe_name='Boiled plantain snack',
            date=date.today() + timedelta(days=1),
            meal_type='snack',
            servings=1,
        )
        MealIngredient.objects.create(
            meal=meal,
            ingredient=self.ingredient,
            name='Plantain',
            quantity=300,
            unit='g',
            unit_price_xaf=2,
        )
        analysis = MealAnalysisService().analyze(meal)
        self.assertEqual(analysis.status, MealAnalysis.Status.LOCAL)
        self.assertFalse(analysis.is_estimated)
        self.assertEqual(analysis.calories, 300)
        self.assertEqual(float(analysis.estimated_total_cost_xaf), 600.0)

    @override_settings(OPENAI_API_KEY='')
    def test_unknown_custom_ingredient_uses_advisory_fallback_without_raw_prompt_storage(self):
        meal = Meal.objects.create(
            meal_plan=self.plan,
            entry_type='custom',
            recipe_name='Fried plantain and eggs',
            date=date.today() + timedelta(days=1),
            meal_type='dinner',
            servings=1,
        )
        MealIngredient.objects.create(meal=meal, name='Eggs', quantity=3, unit='pcs', unit_price_xaf=150)
        analysis = MealAnalysisService().analyze(meal)
        self.assertEqual(analysis.status, MealAnalysis.Status.FALLBACK)
        self.assertTrue(analysis.is_estimated)
        log = AIInteractionLog.objects.filter(operation='meal_analysis', user=self.user).latest('created_at')
        self.assertEqual(log.status, AIInteractionLog.Status.FALLBACK)
        self.assertFalse(hasattr(log, 'prompt'))
        self.assertFalse(hasattr(log, 'response'))

    def test_create_single_day_meal_plan_auto_sets_end_date(self):
        self.client.force_login(self.user)
        start = date.today() + timedelta(days=20)
        response = self.client.post(
            reverse('meals:create'),
            {
                'title': 'One day plan',
                'planning_period': 'single_day',
                'start_date': start.isoformat(),
                'weekly_budget_xaf': 5000,
            },
        )
        self.assertEqual(response.status_code, 302)
        plan = MealPlan.objects.get(title='One day plan')
        self.assertEqual(plan.end_date, start)

    def test_view_can_add_custom_meal_and_auto_analyze(self):
        self.client.force_login(self.user)
        meal_date = date.today() + timedelta(days=2)
        response = self.client.post(
            reverse('meals:detail', args=[self.plan.pk]),
            {
                'entry_type': 'custom',
                'recipe_name': 'Fried plantain and eggs',
                'date': meal_date.isoformat(),
                'meal_type': 'lunch',
                'servings': 1,
                'notes': 'Lunch test',
                'ingredient_id[]': ['', ''],
                'ingredient_name[]': ['Plantain', 'Eggs'],
                'ingredient_quantity[]': ['300', '3'],
                'ingredient_unit[]': ['g', 'pcs'],
                'ingredient_unit_price_xaf[]': ['2', '150'],
            },
        )
        self.assertEqual(response.status_code, 302)
        meal = Meal.objects.get(meal_plan=self.plan, date=meal_date, meal_type='lunch')
        self.assertEqual(meal.entry_type, 'custom')
        self.assertEqual(meal.custom_ingredients.count(), 2)
        self.assertTrue(hasattr(meal, 'analysis'))

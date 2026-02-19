// ignore_for_file: use_build_context_synchronously, deprecated_member_use

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/glass_container.dart';
import '../../providers/onboarding_provider.dart';

class OnboardingWizard extends ConsumerWidget {
  const OnboardingWizard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentStep = ref.watch(onboardingStepProvider);

    Widget buildStep(int step) {
      switch (step) {
        case 0:
          return _AccountStep();
        case 1:
          return _PersonalInfoStep();
        case 2:
          return _GoalsStep();
        case 3:
          return _PreferencesStep();
        case 4:
          return _AllergiesStep();
        default:
          return const Center(child: Text('Invalid Step'));
      }
    }

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppColors.background,
              AppColors.surface.withValues(alpha: 0.8),
            ],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(context, currentStep, ref),
                const SizedBox(height: 32),
                Expanded(child: buildStep(currentStep)),
                const SizedBox(height: 24),
                _buildFooter(context, currentStep, ref, 5),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context, int currentStep, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            if (currentStep > 0)
              IconButton(
                onPressed: () =>
                    ref.read(onboardingStepProvider.notifier).previousStep(),
                icon: const Icon(
                  Icons.arrow_back_ios_new_rounded,
                  color: AppColors.textPrimary,
                ),
              )
            else
              const SizedBox(width: 48),
            Text(
              'Step ${currentStep + 1} of 5',
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(width: 48),
          ],
        ),
        const SizedBox(height: 20),
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: LinearProgressIndicator(
            value: (currentStep + 1) / 5,
            backgroundColor: AppColors.surface,
            color: AppColors.primary,
            minHeight: 8,
          ),
        ),
      ],
    );
  }

  Widget _buildFooter(
    BuildContext context,
    int currentStep,
    WidgetRef ref,
    int totalSteps,
  ) {
    return ElevatedButton(
      onPressed: () async {
        final data = ref.read(onboardingProvider);

        // Validation for Account Step
        if (currentStep == 0) {
          if (data.name.isEmpty ||
              data.email.isEmpty ||
              data.password.isEmpty) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Please fill in all account fields'),
              ),
            );
            return;
          }
          if (data.password != data.confirmPassword) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Passwords do not match')),
            );
            return;
          }
        }

        if (currentStep < totalSteps - 1) {
          ref.read(onboardingStepProvider.notifier).nextStep();
        } else {
          // Finalize onboarding - Save to Firestore
          try {
            // Perform Account creation and Firestore save
            await ref.read(onboardingProvider.notifier).saveData();
            if (context.mounted) {
              Navigator.of(context).pushReplacementNamed('/main');
            }
          } catch (e) {
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Error saving profile: $e')),
              );
            }
          }
        }
      },
      child: Text(currentStep == totalSteps - 1 ? 'Get Started' : 'Next Step'),
    );
  }
}

class _AccountStep extends ConsumerStatefulWidget {
  @override
  ConsumerState<_AccountStep> createState() => _AccountStepState();
}

class _AccountStepState extends ConsumerState<_AccountStep> {
  late TextEditingController _nameController;
  late TextEditingController _emailController;
  late TextEditingController _passwordController;
  late TextEditingController _confirmPasswordController;

  @override
  void initState() {
    super.initState();
    final data = ref.read(onboardingProvider);
    _nameController = TextEditingController(text: data.name);
    _emailController = TextEditingController(text: data.email);
    _passwordController = TextEditingController(text: data.password);
    _confirmPasswordController = TextEditingController(
      text: data.confirmPassword,
    );
  }

  void _updateData() {
    ref
        .read(onboardingProvider.notifier)
        .updateAccountInfo(
          name: _nameController.text,
          email: _emailController.text,
          password: _passwordController.text,
          confirmPassword: _confirmPasswordController.text,
        );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Create Account',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Let\'s start with your basic account details.',
          style: TextStyle(color: AppColors.textSecondary),
        ),
        const SizedBox(height: 32),
        _buildInputField(
          'Full Name',
          'John Doe',
          _nameController,
          icon: Icons.person_outline,
        ),
        const SizedBox(height: 16),
        _buildInputField(
          'Email Address',
          'john@example.com',
          _emailController,
          icon: Icons.email_outlined,
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 16),
        _buildInputField(
          'Password',
          '••••••••',
          _passwordController,
          icon: Icons.lock_outline,
          isPassword: true,
        ),
        const SizedBox(height: 16),
        _buildInputField(
          'Confirm Password',
          '••••••••',
          _confirmPasswordController,
          icon: Icons.lock_outline,
          isPassword: true,
        ),
      ],
    );
  }

  Widget _buildInputField(
    String label,
    String hint,
    TextEditingController controller, {
    IconData? icon,
    bool isPassword = false,
    TextInputType? keyboardType,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          onChanged: (_) => _updateData(),
          obscureText: isPassword,
          keyboardType: keyboardType,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: icon != null
                ? Icon(icon, color: AppColors.textSecondary)
                : null,
          ),
        ),
      ],
    );
  }
}

class _PersonalInfoStep extends ConsumerStatefulWidget {
  @override
  ConsumerState<_PersonalInfoStep> createState() => _PersonalInfoStepState();
}

class _PersonalInfoStepState extends ConsumerState<_PersonalInfoStep> {
  late TextEditingController _ageController;
  late TextEditingController _weightController;
  late TextEditingController _heightController;

  @override
  void initState() {
    super.initState();
    final data = ref.read(onboardingProvider);
    _ageController = TextEditingController(text: data.age.toString());
    _weightController = TextEditingController(text: data.weight.toString());
    _heightController = TextEditingController(text: data.height.toString());
  }

  void _updateData() {
    ref
        .read(onboardingProvider.notifier)
        .updatePersonalInfo(
          age: int.tryParse(_ageController.text),
          weight: double.tryParse(_weightController.text),
          height: double.tryParse(_heightController.text),
        );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Personal Info',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Help us understand your physique better.',
          style: TextStyle(color: AppColors.textSecondary),
        ),
        const SizedBox(height: 32),
        _buildInputField('Age', 'e.g. 25', _ageController),
        const SizedBox(height: 16),
        _buildInputField('Weight (kg)', 'e.g. 70', _weightController),
        const SizedBox(height: 16),
        _buildInputField('Height (cm)', 'e.g. 175', _heightController),
      ],
    );
  }

  Widget _buildInputField(
    String label,
    String hint,
    TextEditingController controller,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          onChanged: (_) => _updateData(),
          decoration: InputDecoration(hintText: hint),
          keyboardType: TextInputType.number,
        ),
      ],
    );
  }
}

class _GoalsStep extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedGoal = ref.watch(onboardingProvider).goal;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Your Goals',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'What are you looking to achieve?',
          style: TextStyle(color: AppColors.textSecondary),
        ),
        const SizedBox(height: 32),
        _buildGoalOption(
          ref,
          'Weight Loss',
          'Burn fat and improve health',
          Icons.trending_down_rounded,
          selectedGoal == 'Weight Loss',
        ),
        _buildGoalOption(
          ref,
          'Muscle Gain',
          'Build strength and size',
          Icons.fitness_center_rounded,
          selectedGoal == 'Muscle Gain',
        ),
        _buildGoalOption(
          ref,
          'Maintenance',
          'Keep your current physique',
          Icons.balance_rounded,
          selectedGoal == 'Maintenance',
        ),
      ],
    );
  }

  Widget _buildGoalOption(
    WidgetRef ref,
    String title,
    String subtitle,
    IconData icon,
    bool isSelected,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: GestureDetector(
        onTap: () => ref.read(onboardingProvider.notifier).updateGoal(title),
        child: GlassContainer(
          padding: const EdgeInsets.all(16),
          borderWidth: isSelected ? 2.0 : 1.5,
          borderColor: isSelected ? AppColors.primary : AppColors.glassBorder,
          child: Row(
            children: [
              Icon(
                icon,
                color: isSelected ? AppColors.primary : AppColors.textSecondary,
                size: 32,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                isSelected
                    ? Icons.check_circle_rounded
                    : Icons.radio_button_unchecked_rounded,
                color: isSelected ? AppColors.primary : AppColors.textSecondary,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PreferencesStep extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedPrefs = ref.watch(onboardingProvider).preferences;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Dietary Preferences',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Select your preferred eating style.',
          style: TextStyle(color: AppColors.textSecondary),
        ),
        const SizedBox(height: 32),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            _buildPrefChip(ref, 'Keto', selectedPrefs.contains('Keto')),
            _buildPrefChip(ref, 'Vegan', selectedPrefs.contains('Vegan')),
            _buildPrefChip(ref, 'Paleo', selectedPrefs.contains('Paleo')),
            _buildPrefChip(
              ref,
              'Vegetarian',
              selectedPrefs.contains('Vegetarian'),
            ),
            _buildPrefChip(ref, 'Low Carb', selectedPrefs.contains('Low Carb')),
            _buildPrefChip(ref, 'Moderate', selectedPrefs.contains('Moderate')),
          ],
        ),
      ],
    );
  }

  Widget _buildPrefChip(WidgetRef ref, String label, bool isSelected) {
    return GestureDetector(
      onTap: () =>
          ref.read(onboardingProvider.notifier).togglePreference(label),
      child: GlassContainer(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        borderRadius: 30,
        borderWidth: isSelected ? 2.0 : 1.5,
        borderColor: isSelected ? AppColors.primary : AppColors.glassBorder,
        child: Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.w600,
            color: isSelected ? AppColors.primary : AppColors.textPrimary,
          ),
        ),
      ),
    );
  }
}

class _AllergiesStep extends ConsumerStatefulWidget {
  @override
  ConsumerState<_AllergiesStep> createState() => _AllergiesStepState();
}

class _AllergiesStepState extends ConsumerState<_AllergiesStep> {
  late TextEditingController _allergyController;

  @override
  void initState() {
    super.initState();
    _allergyController = TextEditingController(
      text: ref.read(onboardingProvider).allergies.join(', '),
    );
  }

  void _updateAllergies(String value) {
    final allergies = value
        .split(',')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();
    ref.read(onboardingProvider.notifier).updateAllergies(allergies);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Allergies',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Safety first! Any allergies we should know about?',
          style: TextStyle(color: AppColors.textSecondary),
        ),
        const SizedBox(height: 32),
        _buildInputField(
          'Any allergies?',
          'e.g. Peanuts, Shellfish...',
          _allergyController,
        ),
        const SizedBox(height: 24),
        const Text(
          'We will use this to filter recipes and meal plans automatically.',
          style: TextStyle(
            color: AppColors.textSecondary,
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }

  Widget _buildInputField(
    String label,
    String hint,
    TextEditingController controller,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          onChanged: _updateAllergies,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: const Icon(
              Icons.warning_amber_rounded,
              color: AppColors.accent,
            ),
          ),
        ),
      ],
    );
  }
}

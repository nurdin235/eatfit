import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/onboarding_data.dart';

class OnboardingNotifier extends Notifier<OnboardingData> {
  @override
  OnboardingData build() {
    return const OnboardingData();
  }

  void updateAccountInfo({
    String? name,
    String? email,
    String? password,
    String? confirmPassword,
  }) {
    state = state.copyWith(
      name: name,
      email: email,
      password: password,
      confirmPassword: confirmPassword,
    );
  }

  void updatePersonalInfo({
    int? age,
    String? gender,
    double? weight,
    double? height,
  }) {
    state = state.copyWith(
      age: age,
      gender: gender,
      weight: weight,
      height: height,
    );
  }

  void updateGoal(String goal) {
    state = state.copyWith(goal: goal);
  }

  void updatePreferences(List<String> preferences) {
    state = state.copyWith(preferences: preferences);
  }

  void togglePreference(String preference) {
    final current = List<String>.from(state.preferences);
    if (current.contains(preference)) {
      current.remove(preference);
    } else {
      current.add(preference);
    }
    state = state.copyWith(preferences: current);
  }

  void updateAllergies(List<String> allergies) {
    state = state.copyWith(allergies: allergies);
  }

  Future<void> saveData() async {
    // 1. Create User in Firebase Auth
    final userCredential = await FirebaseAuth.instance
        .createUserWithEmailAndPassword(
          email: state.email,
          password: state.password,
        );

    final uid = userCredential.user?.uid;
    if (uid == null) throw Exception('User creation failed: UID is null');

    // 2. Save additional data to Firestore
    final docRef = FirebaseFirestore.instance.collection('users').doc(uid);
    await docRef.set({
      'personalInfo': {
        'name': state.name,
        'email': state.email,
        'age': state.age,
        'gender': state.gender,
        'weight': state.weight,
        'height': state.height,
      },
      'goals': {'primaryGoal': state.goal},
      'preferences': {'dietType': state.preferences},
      'allergies': state.allergies,
      'createdAt': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
  }
}

final onboardingProvider = NotifierProvider<OnboardingNotifier, OnboardingData>(
  OnboardingNotifier.new,
);

class OnboardingStepNotifier extends Notifier<int> {
  @override
  int build() => 0;

  void setStep(int step) => state = step;
  void nextStep() => state++;
  void previousStep() => state--;
}

final onboardingStepProvider = NotifierProvider<OnboardingStepNotifier, int>(
  OnboardingStepNotifier.new,
);

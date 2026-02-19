class OnboardingData {
  final String name;
  final String email;
  final String password;
  final String confirmPassword;
  final int age;
  final String gender;
  final double weight;
  final double height;
  final String goal;
  final List<String> preferences;
  final List<String> allergies;

  const OnboardingData({
    this.name = '',
    this.email = '',
    this.password = '',
    this.confirmPassword = '',
    this.age = 25,
    this.gender = 'Other',
    this.weight = 70.0,
    this.height = 170.0,
    this.goal = 'Maintenance',
    this.preferences = const [],
    this.allergies = const [],
  });

  OnboardingData copyWith({
    String? name,
    String? email,
    String? password,
    String? confirmPassword,
    int? age,
    String? gender,
    double? weight,
    double? height,
    String? goal,
    List<String>? preferences,
    List<String>? allergies,
  }) {
    return OnboardingData(
      name: name ?? this.name,
      email: email ?? this.email,
      password: password ?? this.password,
      confirmPassword: confirmPassword ?? this.confirmPassword,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      weight: weight ?? this.weight,
      height: height ?? this.height,
      goal: goal ?? this.goal,
      preferences: preferences ?? this.preferences,
      allergies: allergies ?? this.allergies,
    );
  }
}

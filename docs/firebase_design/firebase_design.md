# Firebase & Database Design - EatFits

This document outlines the architecture for data storage and user management in the EatFits application using Firebase.

## Firestore Database Schema

Firestore will be used as the primary NoSQL document database.

### 1. `users` Collection
Stores user profiles and nutritional targets.

| Field | Type | Description |
|-------|------|-------------|
| `uid` | String | Unique identifier from Firebase Auth |
| `email` | String | User's email |
| `personalInfo` | Map | `{ age, gender, weight, height }` |
| `goals` | Map | `{ targetWeight, activityLevel, primaryGoal }` |
| `preferences` | Map | `{ dietType: "Keto", caloriesTarget: 2200 }` |
| `allergies` | Array | `["Peanuts", "Shellfish"]` |
| `createdAt` | Timestamp | Account creation date |

### 2. `recipes` Collection
Global and user-added recipes.

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Recipe ID |
| `title` | String | Recipe name |
| `ingredients` | Array | Objects: `{ name, quantity, unit }` |
| `macros` | Map | `{ calories, protein, carbs, fats }` |
| `dietTags` | Array | `["Vegan", "Gluten-Free"]` |
| `isPublic` | Boolean | Visibility |
| `ownerId` | String | UID of the creator |

### 3. `meal_plans` Collection
Weekly schedules for users.

| Field | Type | Description |
|-------|------|-------------|
| `userId` | String | Reference to user |
| `weekStarting` | Date | Monday of the week |
| `days` | Map | `{ "Monday": { "breakfast": id, "lunch": id, "dinner": id } }` |

## Firebase Storage Structure

Firebase Storage will manage binary assets.

- `users/{uid}/profile_pic.jpg`: User profile image.
- `recipes/{recipeId}/image.jpg`: High-quality recipe photos.

## Security Rules Strategy

1. **Users**: Users can only read/write their own document in the `users` collection.
2. **Recipes**: Public recipes are read-only for all. Private recipes are restricted to the owner.
3. **Storage**: Authenticated users can write to their own `users/{uid}/` folder.

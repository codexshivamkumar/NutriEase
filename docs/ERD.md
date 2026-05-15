# NutriEase — Entity Relationship Diagram

```
+-----------+        +-----------+        +--------------+
|   users   |1------1|  profiles |        | weight_logs  |
+-----------+        +-----------+        +--------------+
   1   1                                       *
   |   |                                       |
   *   |                                       |
+-------+   +---------+   +------------------+ |
| diet_ |   | reminders|  | deficiency_reports| |
| plans |   +---------+   +------------------+ |
+-------+        *               *             |
   *             |               |             |
+-----------+   +-----------+   +-----------+  |
|conversations|1*|messages |   | password_reset_otps |
+-----------+   +-----------+   +-----------+
```

- `users` is the parent entity. All per-user records are deleted when a user is removed (`ON DELETE CASCADE`).
- `conversations` has many `messages` ordered by `created_at`.
- `password_reset_otps` is keyed by `email` rather than `user_id` so that requests for unknown emails behave identically (anti-enumeration).

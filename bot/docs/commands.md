# 📘 Bot Commands Documentation

This bot provides real-time NBA statistics and information. Below is a list of available commands, their usage, and example outputs.

## 📊 `!record`

**Description**: Get the current season win-loss record for an NBA team.

**Usage**:
```
!record <team name>
```

**Example**:
```
!record Lakers
```

**Bot Response**:
```
@user Lakers are currently 45-29 (3rd in Western Conference).
```

---

## 🏀 `!score`

**Description**: Check the current game score for an NBA team if they are playing today.

**Usage**:
```
!score <team name>
```

**Example**:
```
!score Celtics
```

**Bot Response (if playing)**:
```
@user Celtics are leading the Knicks 102-95 with 3:45 left in the 4th quarter.
```

**Bot Response (if not playing)**:
```
@user The Celtics are not currently playing.
```

---

## 📈 `!stats`

**Description**: Get the latest game stat line for a specific NBA player.

**Usage**:
```
!stats <player name>
```

**Example**:
```
!stats Kevin Durant
```

**Bot Response**:
```
@user Kevin Durant: 29 PTS, 8 REB, 5 AST, 2 STL, 1 BLK (Final)
```

---

## 🆘 `!help`

**Description**: Provides a link to the full list of available bot commands.

**Usage**:

---

## ⏱ Cooldown

All commands have a **per-channel cooldown** of 5 seconds to prevent spam.

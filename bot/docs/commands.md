# NBALiveBot Commands

This bot provides real-time NBA statistics. Below is a list of available commands, their usage, and example outputs.

## `!record`

**Description**: Get the current season win-loss record for an NBA team.

**Usage**:
```
!record <team name>
```

**Example**:
```
!record Lakers or !record LAL or !record Los Angeles Lakers
```

**Bot Response**:
```
@username The Los Angeles Lakers are 50 - 32
```

---

## `!score`

**Description**: Check the current game score for an NBA team if they are playing today.

**Usage**:
```
!score <team name>
```

**Example**:
```
!score Celtics or !score BOS or !score Boston Celtics
```

**Bot Response**:
```
@username Boston Celtics 120 - Orlando Magic 89 (Final)
```

---

## `!stats`

**Description**: Get the latest game stat line for a specific NBA player.

**Usage**:
```
!stats <player name>
```

**Example**:
```
!stats Anthony Edwards
```

**Bot Response**:
```
@username Anthony Edwards: 29 PTS, 8 REB, 5 AST, 2 STL, 1 BLK (Final)
```

---

## `!commands`

**Description**: Provides a link to the full list of available bot commands.

**Usage**:
```
!commands
```

**Bot Response**:
```
@username https://github.com/ken862734801/nba-live-bot/blob/main/bot/docs/commands.md
```

---

## Cooldown

All commands have a **per-channel cooldown** of 5 seconds to prevent spam.

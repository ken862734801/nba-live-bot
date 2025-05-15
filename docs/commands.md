# NBALiveBot Commands

This bot provides real-time NBA statistics. Below is a list of available commands, their usage, and example outputs.

## `!career`

**Description**: Get the career statistics of a specific player.

**Usage**:
```
!career <player name>
```

**Example**:
```
!career Donovan Mitchell
```

**Bot Response**:
```
@username Donovan Mitchell: 24.7 PTS, 4.3 REB, 4.7 AST, 44.9%
```

---

## `!commands`

**Description**: Provides a link to the full list of available bot commands.

**Usage**:
```
!commands
```

**Example**:
```
!commands
```

**Bot Response**:
```
@username https://github.com/ken862734801/nba-live-bot/blob/main/bot/docs/commands.md
```

---

## `!record`

**Description**: Get the current season win-loss record for an NBA team.

**Usage**:
```
!record <team_name>
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

## `!schedule`

**Description**: Get the NBA schedule for the current day.

**Usage**
```
!schedule
```

**Example**
```
!schedule
```

**Bot Response**
```
@username May 5th: BOS @ MIA (8 PM EST), NYK @ PHI (8 PM EST)
```

---

## `!score`

**Description**: Check the current game score for an NBA team if they are playing today.

**Usage**:
```
!score <team_name>
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

## `!statline`

**Description**: Get the live statline for a specific NBA player.

**Usage**:
```
!stats <player_name>
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

## Cooldown

All commands have a **per-channel cooldown** of 5 seconds to prevent spam.
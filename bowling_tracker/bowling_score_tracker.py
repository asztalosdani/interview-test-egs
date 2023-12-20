from enum import Enum
from typing import List, Optional


class Shot(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9

    STRIKE = "X"
    SPARE = "/"

    @staticmethod
    def from_string(string: str) -> Optional['Shot']:
        if string.isnumeric():
            return Shot(int(string))
        elif string in ("x", "X",):
            return Shot.STRIKE
        elif string == "/":
            return Shot.SPARE

        return None


class ShotInvalidException(Exception):

    def __init__(self, shot: Shot):
        self.shot = shot


class BowlingScoreTracker:

    def __init__(self):
        self._shots: List[Shot] = []
        self._current_frame = 0
        self._current_shot = 0
        self._game_over = False

    @property
    def current_frame(self) -> int:
        return self._current_frame

    @property
    def current_shot(self) -> int:
        return self._current_shot

    @property
    def game_over(self) -> bool:
        return self._game_over

    def shoot(self, shot: Shot):
        if self._is_invalid_shot(shot):
            raise ShotInvalidException(shot)

        self._shots.append(shot)

        self._advance_game_progress(shot)

    def _is_invalid_shot(self, shot: Shot) -> bool:
        # do not allow Spares as first shots, Strikes as second shots, and shots with sum >= 10
        return (shot is Shot.SPARE and self._current_shot == 0
                or shot is Shot.STRIKE and self._current_shot != 0 and self._current_frame != 9
                or shot not in (Shot.STRIKE, Shot.SPARE) and self._shots and self._shots[-1] not in (Shot.STRIKE, Shot.SPARE) and self._current_shot != 0 and shot.value + self._shots[-1].value >= 10)

    def _advance_game_progress(self, shot: Shot):
        if self._current_shot == 0:
            if shot is Shot.STRIKE and self._current_frame != 9:
                self._current_frame += 1
            else:
                self._current_shot += 1
        else:
            if self._current_frame != 9:
                self._current_shot = 0
                self._current_frame += 1
            else:
                if (self._current_shot == 1 and self._is_frame_open(self._current_frame)
                        or self._current_shot == 2):
                    self._game_over = True
                    self._current_frame = -1
                else:
                    self._current_shot += 1

    def _is_frame_open(self, frame: int):
        shots_by_frame = self.get_shots_by_frame()
        shots_in_frame = shots_by_frame[frame]
        return Shot.STRIKE not in shots_in_frame and Shot.SPARE not in shots_in_frame

    def reset(self):
        self._shots = []
        self._current_frame = 0
        self._current_shot = 0
        self._game_over = False

    def get_shots_by_frame(self):
        result = []
        frame_number = 0
        shot_number = 0
        frame = []

        for shot in self._shots:
            if shot_number == 0:
                frame.append(shot)

                if shot is Shot.STRIKE and frame_number != 9:
                    result.append(frame)
                    frame_number += 1
                    shot_number = 0
                    frame = []
                else:
                    shot_number += 1
            else:
                frame.append(shot)

                if frame_number == 9:
                    shot_number += 1
                else:
                    result.append(frame)
                    frame_number += 1
                    shot_number = 0
                    frame = []

        if frame:  # intermediate frame
            result.append(frame)

        return result

    def get_scores(self) -> List[int]:
        result = []
        cumulative_score = 0
        current_frame = 0
        current_shot = 0
        current_frame_score = 0
        frame_closed = False

        for i, shot in enumerate(self._shots):
            if shot is Shot.STRIKE:
                current_frame_score += 10 + self._shot_score(i + 1) + self._shot_score(i + 2)
                frame_closed = True
            elif shot is Shot.SPARE:
                current_frame_score = 10 + self._shot_score(i + 1)
                frame_closed = True
            else:
                if current_shot == 0:
                    current_frame_score = shot.value
                    current_shot += 1

                    if i == len(self._shots) - 1:  # intermediate score for the frame
                        frame_closed = True
                else:
                    current_frame_score += shot.value
                    frame_closed = True

            if frame_closed:
                frame_closed = False
                cumulative_score += current_frame_score
                result.append(cumulative_score)
                if current_frame == 9:
                    current_shot += 1
                else:
                    current_frame += 1
                    current_shot = 0
                    current_frame_score = 0

        return result

    def _shot_score(self, i: int) -> int:
        if i < len(self._shots):
            shot = self._shots[i]
            if shot is Shot.STRIKE:
                return 10
            elif shot is Shot.SPARE:
                return 10 - self._shot_score(i - 1)
            else:
                return shot.value
        else:
            return 0

def validate_intervals_timings(intervals_timings: list[int]) -> list[int]:
    pupil_start_intervals: list[int] = sorted(intervals_timings[::2])
    pupil_end_intervals: list[int] = sorted(intervals_timings[1::2])

    new_pupil_intervals: list[int] = []
    l = 0
    while l < len(pupil_end_intervals):
        new_pupil_intervals += [pupil_start_intervals[l]]
        
        while l + 1 < len(pupil_start_intervals) and pupil_start_intervals[l + 1] < pupil_end_intervals[l]:
            l += 1
        
        new_pupil_intervals += [pupil_end_intervals[l]]
        l += 1

    return new_pupil_intervals


def appearance(intervals: dict[str, list[int]]) -> int:
    LESSON, PUPIL, TUTOR = "lesson", "pupil", "tutor"
    interval_types: list[str] = [LESSON, PUPIL, TUTOR]

    # !!! Блок Валидации входных данных !!!

    # 1) Проверка наличия всех типов интервалов
    for interval_type in interval_types:
        if interval_type not in intervals:
            raise ValueError(f"Отсутствуют интервалы для ключа {interval_type}")

    # 2) Размеры интервалов должны быть кратным 2
    if len(intervals[LESSON]) != 2 \
       or len(intervals[PUPIL]) % 2 != 0 \
        or len(intervals[TUTOR]) % 2 != 0:
        raise ValueError("Интервалы должны быть четного размера")
    
    # 3) Проверка корректности интервалов
    if intervals[LESSON][0] > intervals[LESSON][1]:
        raise ValueError("Начало урока не может быть больше конца урока")
    
    # Валидируем интвервалы ученика и репетитора
    intervals[PUPIL] = validate_intervals_timings(intervals[PUPIL])
    intervals[TUTOR] = validate_intervals_timings(intervals[TUTOR])

    # Поиск пересечений интервалов
    union_apperance_time = 0
    tutor_l, pupil_l = 0, 0
    while tutor_l < len(intervals[TUTOR]) and pupil_l < len(intervals[PUPIL]):
        # Получаем начало и конец интервалов
        lesson_start, lesson_end = intervals[LESSON][0], intervals[LESSON][1]
        pupil_start, pupil_end = intervals[PUPIL][pupil_l], intervals[PUPIL][pupil_l + 1]
        tutor_start, tutor_end = intervals[TUTOR][tutor_l], intervals[TUTOR][tutor_l + 1]

        # Проверяем пересечение интервалов
        if lesson_start <= pupil_end and lesson_end >= pupil_start and \
           lesson_start <= tutor_end and lesson_end >= tutor_start:
            union_apperance_time += min(lesson_end, pupil_end, tutor_end) - max(lesson_start, pupil_start, tutor_start)

        # Сдвигаем указатели
        if pupil_end < tutor_end:
            pupil_l += 2
        else:
            tutor_l += 2

    return union_apperance_time

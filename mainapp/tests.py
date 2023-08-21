from django.test import TestCase

from mainapp.services import PreprocessingRawString, PreprocessingRawStringV2


class PreprocessingRawStringV2TestCase(TestCase):
    def test_split(self):
        """ Протестирует разделение строки на ячейки. """
        line_1 = (
            '";11874964662";(null);"Иванов ИВАН иванович";(null)";РЛИД;";"00;7";[2004/05/03];"null";"""б/н""";"""Китайский районный суд; Администрация Пекина""";'
            '[2004/05/23]')
        line_2 = '11111111111;22222222222;Иванов ИВАН иванович;Петров ИВАН иванович;РЗП;021;2021-08-20;null;";441_Ш";"Управления социальной политики № 1";2022-08-20'

        line_3 = r'null;"Администрация МР \"Медынский район\"";2006-03-28'
        line_4 = r'[2004/05/19];"""без серии \\""";"""без номера\\""";"""Тальменский районный суд Алтайского края""";[2004/05/08]'
        line_5 = 'null;"";"Красноармейский районный суд Краснодарского края";2018-03-20'
        line_6 = r'"null";"""ГКУЗ ЯО \""Областной специализированный дом ребенка №1\"" города Ярославля""";[2020/07/21]'
        line_7 = r'null;"Администрация муниципального образования \"Тигильский муниципальный район\"";2020-10-23'
        line_8 = r'"196";"Управление общественных отношений, опеки и попечительства администрации МО ГО \"Воркута\"";2020-05-29'
        line_9 = r'(null);"РЛИД";"007";[2004/05/19];"""без серии \\""";"""без номера\\""";"""Тальменский районный суд Алтайского края"""'
        line_10 = r'"Администрация МО \"Город Нарьян- Мар\"\"";2003-11-21'


        assert_line_1 = '11874964662;null;Иванов ИВАН иванович;nullРЛИД;007;2004/05/03;null;б/н;Китайский районный суд Администрация Пекина;2004/05/23'
        assert_line_2 = '11111111111;22222222222;Иванов ИВАН иванович;Петров ИВАН иванович;РЗП;021;2021-08-20;null;441_Ш;Управления социальной политики № 1;2022-08-20'
        assert_line_3 = 'null;Администрация МР Медынский район;2006-03-28'
        assert_line_4 = r'2004/05/19;без серии ;без номера;Тальменский районный суд Алтайского края;2004/05/08'
        assert_line_5 = 'null;;Красноармейский районный суд Краснодарского края;2018-03-20'
        assert_line_6 = r'null;ГКУЗ ЯО Областной специализированный дом ребенка №1 города Ярославля;2020/07/21'
        assert_line_7 = r'null;Администрация муниципального образования Тигильский муниципальный район;2020-10-23'
        assert_line_8 = r'196;Управление общественных отношений, опеки и попечительства администрации МО ГО Воркута;2020-05-29'
        assert_line_9 = r'null;РЛИД;007;2004/05/19;без серии ;без номера;Тальменский районный суд Алтайского края'
        assert_line_10 = r'Администрация МО Город Нарьян- Мар;2003-11-21'

        processed_line_1 = PreprocessingRawStringV2.process(line_1)
        processed_line_2 = PreprocessingRawStringV2.process(line_2)
        processed_line_3 = PreprocessingRawStringV2.process(line_3)
        processed_line_4 = PreprocessingRawStringV2.process(line_4)
        processed_line_5 = PreprocessingRawStringV2.process(line_5)
        processed_line_6 = PreprocessingRawStringV2.process(line_6)
        processed_line_7 = PreprocessingRawStringV2.process(line_7)
        processed_line_8 = PreprocessingRawStringV2.process(line_8)
        processed_line_9 = PreprocessingRawStringV2.process(line_9)
        processed_line_10 = PreprocessingRawStringV2.process(line_10)

        self.assertEqual(assert_line_1, processed_line_1)
        self.assertEqual(assert_line_2, processed_line_2)
        self.assertEqual(assert_line_3, processed_line_3)
        self.assertEqual(assert_line_4, processed_line_4)
        self.assertEqual(assert_line_5, processed_line_5)
        self.assertEqual(assert_line_6, processed_line_6)
        self.assertEqual(assert_line_7, processed_line_7)
        self.assertEqual(assert_line_8, processed_line_8)
        self.assertEqual(assert_line_9, processed_line_9)
        self.assertEqual(assert_line_10, processed_line_10)

import datetime
from django.test import TestCase
from appointment.models import Appointment
from appointment.services.booking_service import _available_slot_minutes, _add_slots_in_interval
from appointment.services.utils import to_min
from user.models import User


class SlotCalculationTestCase(TestCase):
    """
    Testa se o cálculo de horários disponíveis está funcionando corretamente.
    
    Este teste valida o alinhamento entre backend e frontend para garantir que
    ambos calculam os mesmos slots disponíveis.
    """

    def setUp(self):
        """Cria um usuário para os testes"""
        self.user = User.objects.create_user(
            username='barber_test',
            password='testpass123',
            email='barber@test.com'
        )

    def test_add_slots_in_interval_no_space(self):
        """Testa quando não há espaço para nenhum slot"""
        slots = set()
        _add_slots_in_interval(slots, 0, 30, 60)  # 30min no intervalo, 60min de duração
        self.assertEqual(slots, set())

    def test_add_slots_in_interval_single_slot(self):
        """Testa quando há espaço para exatamente um slot"""
        slots = set()
        _add_slots_in_interval(slots, 0, 60, 60)  # 60min no intervalo, 60min de duração
        self.assertEqual(slots, {0})

    def test_add_slots_in_interval_multiple_slots(self):
        """Testa quando há espaço para múltiplos slots"""
        slots = set()
        _add_slots_in_interval(slots, 480, 660, 30)  # 8:00-11:00 (180min), slots de 30min
        expected = {480, 510, 540, 570, 600, 630}
        self.assertEqual(slots, expected)

    def test_natural_continuation_12_30_to_13_00_with_50min_service(self):
        """
        Testa o caso específico mencionado no issue:
        - Agendamento 12:30-13:00 (30 minutos)
        - Serviço de 50 minutos
        - Próximo slot disponível deve ser 13:00
        
        12:30 = 750 minutos
        13:00 = 780 minutos
        13:50 = 830 minutos
        """
        # Simula um agendamento 12:30-13:00 (750-780 min)
        appointment = type('obj', (object,), {
            'time': datetime.time(12, 30),
            'duration': 30
        })

        # Calcula slots disponíveis de 9:00 a 18:00 (540-1080 min) com duração de 50 min
        available_slots = _available_slot_minutes(
            start_min=540,      # 09:00
            end_min=1080,       # 18:00
            duration=50,
            appointments=[appointment]
        )

        # Converte para formato HH:MM para comparação
        slot_13_00 = to_min("13:00")  # 780
        self.assertIn(slot_13_00, available_slots, 
                      "O horário 13:00 deve estar disponível após agendamento 12:30-13:00")

    def test_no_overlap_available_slots(self):
        """
        Testa que não há slots sobrepostos com agendamentos existentes
        """
        appointment = type('obj', (object,), {
            'time': datetime.time(10, 0),
            'duration': 60
        })

        available_slots = _available_slot_minutes(
            start_min=540,      # 09:00
            end_min=1080,       # 18:00
            duration=30,
            appointments=[appointment]
        )

        slot_10_00 = to_min("10:00")  # 600
        slot_10_30 = to_min("10:30")  # 630
        
        self.assertNotIn(slot_10_00, available_slots,
                         "10:00 não deve estar disponível (conflita com 10:00-11:00)")
        self.assertNotIn(slot_10_30, available_slots,
                         "10:30 não deve estar disponível (conflita com 10:00-11:00)")

    def test_slot_after_appointment_is_available(self):
        """
        Testa que um slot pode começar exatamente quando um agendamento termina
        (implementação da "continuação natural")
        """
        appointment = type('obj', (object,), {
            'time': datetime.time(10, 0),
            'duration': 30
        })

        available_slots = _available_slot_minutes(
            start_min=540,      # 09:00
            end_min=1080,       # 18:00
            duration=30,
            appointments=[appointment]
        )

        slot_10_30 = to_min("10:30")  # 630 (10:30)
        self.assertIn(slot_10_30, available_slots,
                      "10:30 deve estar disponível (continuação natural após 10:00-10:30)")

    def test_multiple_appointments_create_correct_gaps(self):
        """
        Testa que múltiplos agendamentos criam gaps corretos
        """
        appt1 = type('obj', (object,), {
            'time': datetime.time(10, 0),
            'duration': 30
        })
        appt2 = type('obj', (object,), {
            'time': datetime.time(11, 0),
            'duration': 30
        })

        available_slots = _available_slot_minutes(
            start_min=540,      # 09:00
            end_min=1080,       # 18:00
            duration=30,
            appointments=[appt1, appt2]
        )

        # Deve ter slots em:
        # 09:00, 09:30 (antes de 10:00-10:30)
        # 10:30 (natural continuation)
        # 11:30, 12:00, ..., 17:30 (depois de 11:00-11:30)

        self.assertIn(to_min("09:00"), available_slots)
        self.assertIn(to_min("09:30"), available_slots)
        self.assertIn(to_min("10:30"), available_slots)
        self.assertIn(to_min("11:30"), available_slots)
        self.assertIn(to_min("17:30"), available_slots)


if __name__ == '__main__':
    import unittest
    unittest.main()

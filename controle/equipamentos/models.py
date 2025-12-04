from django.db import models
# Importamos as opções de status do app de dispositivos para manter consistência
from dispositivos.models import STATUS_CHOICES

TIPO_EQUIPAMENTO_AUX_CHOICES = [
    ('MOUSE', 'Mouse'),
    ('TECLADO', 'Teclado'),
    ('HEADSET', 'Headset'),
    ('MONITOR', 'Monitor'),
]

class EquipamentoAuxiliar(models.Model):
    nome = models.CharField(max_length=100)
    tipo_equipamento_aux = models.CharField(max_length=20, choices=TIPO_EQUIPAMENTO_AUX_CHOICES)
    
    # MUDANÇA: De pessoa para funcionario (referência via string)
    funcionario = models.ForeignKey(
        'funcionarios.Funcionario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='equipamentos' # Permite: funcionario.equipamentos.all()
    )
    
    # Referência ao Dispositivo (referência via string)
    dispositivo = models.ForeignKey(
        'dispositivos.Dispositivo', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
        # Nota: Não definimos related_name aqui para manter o padrão 'equipamentoauxiliar_set'
        # que você usou na property do model Dispositivo.
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')

    class Meta:
        ordering = ['nome']
        verbose_name = "Equipamento Auxiliar"
        verbose_name_plural = "Equipamentos Auxiliares"

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_equipamento_aux_display()})"

    # -----------------------
    # REGRAS DE STATUS
    # -----------------------

    def save(self, *args, **kwargs):
        # Verifica se tem dono (Funcionario ou Dispositivo vinculado)
        if self.funcionario or self.dispositivo:
            self.status = "ATIVO"
        else:
            self.status = "DISPONIVEL"
        super().save(*args, **kwargs)

    def vincular(self, funcionario=None, dispositivo=None):
        if funcionario:
            self.funcionario = funcionario
        if dispositivo:
            self.dispositivo = dispositivo
        
        # O save() já cuida de atualizar o status para ATIVO
        self.save()

    def desvincular(self):
        self.funcionario = None
        self.dispositivo = None
        # O save() já cuida de atualizar o status para DISPONIVEL
        self.save()
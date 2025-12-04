from django.db import models
from django.utils import timezone 

# As opções permanecem as mesmas
STATUS_CHOICES = [
    ('DISPONIVEL', 'Disponível'),
    ('ATIVO', 'Ativo'),
    ('MANUTENCAO', 'Em manutenção'),
]

TIPO_DISPOSITIVO_CHOICES = [
    ('NOTEBOOK', 'Notebook'),
    ('COLETOR', 'Coletor'),
    ('IMPRESSORA', 'Impressora'),
]

class Dispositivo(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    tipo_dispositivo = models.CharField(max_length=20, choices=TIPO_DISPOSITIVO_CHOICES)
    
    # ALTERAÇÃO PRINCIPAL: Mudamos de Pessoa para Funcionario
    # Usamos 'funcionarios.Funcionario' (nome do app.Model) para evitar erros de importação
    funcionario = models.ForeignKey(
        'funcionarios.Funcionario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='dispositivos' # Permite acessar: funcionario.dispositivos.all()
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')
    status_antes_manutencao = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)

    class Meta:
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.get_tipo_dispositivo_display()}"

    # Propriedade para acessar os equipamentos auxiliares deste dispositivo
    # Isso requer que no model EquipamentoAuxiliar o ForeignKey aponte para 'dispositivo'
    @property
    def equipamentos_auxiliares(self):
        return self.equipamentoauxiliar_set.all()

    # ---------------------
    # REGRAS DE NEGÓCIO
    # ---------------------

    def vincular(self, funcionario):
        self.funcionario = funcionario
        if self.status != 'MANUTENCAO':
            self.status = 'ATIVO'
        self.save()

    def desvincular(self):
        self.funcionario = None
        if self.status != 'MANUTENCAO':
            self.status = 'DISPONIVEL'
        self.save()

    def enviar_manutencao(self):
        if self.status != 'MANUTENCAO':
            self.status_antes_manutencao = self.status
            self.status = 'MANUTENCAO'
            # Ao ir para manutenção, desvinculamos o funcionário? 
            # Se sim, mantenha a linha abaixo. Se não, remova.
            self.funcionario = None 
            self.save()

            ManutencaoDispositivo.objects.create(
                dispositivo=self,
                data_inicio=timezone.now()
            )

    def retornar_da_manutencao(self):
        if self.status == 'MANUTENCAO':
            # Retorna ao status anterior (ou DISPONIVEL se não houver histórico)
            self.status = self.status_antes_manutencao or 'DISPONIVEL'
            self.status_antes_manutencao = None
            self.save()

            # Encerra o registro na tabela de manutenção
            manut = ManutencaoDispositivo.objects.filter(
                dispositivo=self,
                data_fim__isnull=True
            ).last()

            if manut:
                manut.data_fim = timezone.now()
                manut.save()


class ManutencaoDispositivo(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_inicio']
        verbose_name = "Manutenção de Dispositivo"
        verbose_name_plural = "Manutenções de Dispositivos"

    def __str__(self):
        return f"Manutenção {self.dispositivo.codigo} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"
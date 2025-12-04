from django.db import models
from django.utils import timezone

class UnidadeTrabalho(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Funcionario(models.Model):
    STATUS_CHOICES = [
        ("ATIVO", "Ativo"),
        ("DEMITIDO", "Demitido"),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    unidade_trabalho = models.ForeignKey(
        UnidadeTrabalho,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="ATIVO"
    )
    data_admissao = models.DateField(default=timezone.now)
    data_demissao = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"

    def __str__(self):
        return self.nome

    def demitir(self):
        """Marca funcionário como demitido e registra no histórico"""
        self.status = "DEMITIDO"
        self.data_demissao = timezone.now().date()
        self.save()

        HistoricoFuncionario.objects.create(
            funcionario=self,
            acao="DEMITIDO",
            data=timezone.now(),
            descricao=f"{self.nome} foi demitido."
        )

    def reativar(self):
        """Reativa funcionário anteriormente demitido"""
        self.status = "ATIVO"
        self.data_demissao = None
        self.save()

        HistoricoFuncionario.objects.create(
            funcionario=self,
            acao="REATIVADO",
            data=timezone.now(),
            descricao=f"{self.nome} foi reativado."
        )

class HistoricoFuncionario(models.Model):
    ACOES = [
        ("CONTRATADO", "Contratado"),
        ("DEMITIDO", "Demitido"),
        ("REATIVADO", "Reativado"),
        ("TRANSFERIDO", "Transferido de unidade"),
    ]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='historico')
    acao = models.CharField(max_length=20, choices=ACOES)
    data = models.DateTimeField(default=timezone.now)
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-data"]
        verbose_name = "Histórico do Funcionário"
        verbose_name_plural = "Históricos dos Funcionários"

    def __str__(self):
        return f"{self.funcionario.nome} - {self.get_acao_display()}"
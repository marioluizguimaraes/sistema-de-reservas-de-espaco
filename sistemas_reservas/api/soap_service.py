from spyne import Application, rpc, ServiceBase, Integer, Unicode, Array, ComplexModel, DateTime
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, DurationField, ExpressionWrapper
from api.models import Reserva


class SoapReservaRelatorio(ComplexModel):
    """Modelo de resposta para o relatório (com dados do usuário)"""
    id = Integer
    solicitante_nome = Unicode
    solicitante_cpf = Unicode      
    solicitante_celular = Unicode  
    data_inicio = DateTime
    data_fim = DateTime
    status = Unicode
    valor = Unicode
    duracao_horas = Unicode

class RelatorioSoapService(ServiceBase):
    
    @rpc(Integer, Integer, Unicode, _returns=Array(SoapReservaRelatorio))
    def gerar_relatorio_reservas(ctx, sala_id, limite, ordenacao):
        """
        Gera relatório com dados sensíveis do solicitante (CPF/Celular).
        """
        reservas = Reserva.objects.filter(sala_id=sala_id).select_related('solicitante')
        ordenacao = ordenacao.upper() if ordenacao else 'RECENTES'

        if ordenacao == 'ANTIGAS':
            reservas = reservas.order_by('data_inicio')
        elif ordenacao == 'MAIOR_DURACAO':
            reservas = reservas.annotate(duracao=ExpressionWrapper(F('data_fim') - F('data_inicio'),output_field=DurationField())).order_by('-duracao')
        else:
            reservas = reservas.order_by('-data_inicio')

        if limite and limite > 0:
            reservas = reservas[:limite]

        resultado = []
        
        for r in reservas:

            total_segundos = (r.data_fim - r.data_inicio).total_seconds()
            horas = round(total_segundos / 3600, 2)

            resultado.append(SoapReservaRelatorio(
                id=r.id,
                solicitante_nome=r.solicitante.username,

                solicitante_cpf=r.solicitante.cpf,        
                solicitante_celular=r.solicitante.celular,
                
                data_inicio=r.data_inicio,
                data_fim=r.data_fim,
                status=r.status,
                valor=str(r.valor_total) if r.valor_total else "0.00",
                duracao_horas=f"{horas}h"
            ))
            
        return resultado

soap_app = Application([RelatorioSoapService], tns='sistemas.reservas.soap', in_protocol=Soap11(validator='lxml'), out_protocol=Soap11(), )

django_soap_application = DjangoApplication(soap_app)

@csrf_exempt
def soap_view(request):
    return django_soap_application(request)
# 🏗️ Arquitetura de URLs para SaaS de Agendamento

Este documento define a melhor estrutura de URLs, organização de app no Django e exemplos práticos para um sistema SaaS de agendamento onde:

* A página principal (`/`) é uma **landing page de vendas**
* Cada cliente (estabelecimento) possui uma **agenda pública própria**

---

# 🎯 Objetivo

Separar corretamente:

* 🌐 **Site institucional (vendas)**
* 👤 **Sistema do cliente (agenda pública)**

---

# 🏆 Estrutura recomendada de URLs

```bash
/                  → Landing page (vendas)
/login             → Login do cliente
/dashboard         → Painel do cliente

/e/<uid>           → Agenda pública do estabelecimento
/e/<uid>/servicos  → Lista de serviços
/e/<uid>/sobre     → Informações do estabelecimento
```

---

# ❌ O que NÃO fazer

```bash
/<uid>
/home/<uid>
/<uid>/home
```

### Problemas:

* Conflito com rotas da landing page
* URL confusa
* Difícil escalar

---

# 🧠 Conceito usado: Multi-tenant

Cada estabelecimento é um **tenant** dentro do sistema.

👉 O `uid` representa esse tenant.

---

# 🧱 Nome do app Django

Recomendado:

```bash
tenants
```

Alternativas:

* establishments
* business

---

# 🧩 Model (exemplo)

```python
import uuid
from django.db import models

class Establishment(models.Model):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)
```

---

# 🌐 URLs (urls.py)

```python
from django.urls import path
from . import views

urlpatterns = [
    path('e/<str:uid>/', views.public_agenda, name='public_agenda'),
    path('e/<str:uid>/servicos/', views.services, name='services'),
    path('e/<str:uid>/sobre/', views.about, name='about'),
]
```

---

# ⚙️ View (buscar pelo UID)

```python
from django.shortcuts import render, get_object_or_404
from .models import Establishment


def public_agenda(request, uid):
    establishment = get_object_or_404(Establishment, uid=uid)

    context = {
        'establishment': establishment
    }

    return render(request, 'agenda.html', context)
```

---

# 📅 Exemplo com Agenda

```python
from appointments.models import Appointment


def public_agenda(request, uid):
    establishment = get_object_or_404(Establishment, uid=uid)

    appointments = Appointment.objects.filter(
        establishment=establishment
    )

    context = {
        'establishment': establishment,
        'appointments': appointments
    }

    return render(request, 'agenda.html', context)
```

---

# 🔒 Segurança

* UID deve ser **único**
* Não usar ID incremental
* Usar `uuid` ou string aleatória

---

# 🚀 Alternativa avançada (subdomínio)

```bash
<uid>.agendar.com
```

Exemplo:

```bash
5jdhfsfiu2h3.agendar.com
```

### Requisitos:

* DNS com wildcard
* Configuração de host no Django

👉 Mais complexo, usar depois

---

# 🧠 Boas práticas

* URLs curtas
* UID não previsível
* Separação clara entre SaaS e cliente
* Preparar para escalar

---

# 🏁 Resumo final

👉 Estrutura ideal:

```bash
/e/<uid>
```

👉 App Django:

```bash
tenants
```

👉 Benefícios:

* Escalável
* Profissional
* Seguro

---

Se quiser evoluir isso:

* geração de slug personalizado
* painel de administração
* cache de agenda
* APIs

👉 Próximo passo: transformar isso em um sistema SaaS completo 🔥

# Motor de revisões cienciométricas — um pipeline, muitas revisões
# Uso: make ajuda

PY       ?= python3
export PYTHONPATH := src
REVISAO  ?=
SEED     ?=
TRIAGEM  ?=

ARGS = --revisao $(REVISAO) $(if $(SEED),--seed $(SEED),)

.PHONY: ajuda nova listar importar dedup triagem kappa indicadores redes prisma relatorio analise exemplo teste limpar plugin exige-revisao

ajuda:
	@echo "Motor de revisões cienciométricas"
	@echo
	@echo "  make listar                            revisões existentes"
	@echo "  make nova SLUG=<slug> TITULO=\"...\"      cria uma revisão"
	@echo
	@echo "Com REVISAO=<slug>:"
	@echo "  make importar     lê dados/bruto da revisão e monta o corpus"
	@echo "  make dedup        deduplica; separa a faixa de dúvida para conferência"
	@echo "  make triagem      gera a planilha cega de triagem"
	@echo "  make kappa        concordância entre revisores (TRIAGEM=arquivo.csv)"
	@echo "  make indicadores  produção, Lotka, Bradford, Price, impacto, colaboração"
	@echo "  make redes        co-citação, acoplamento, coautoria, co-palavras, mapa temático"
	@echo "  make prisma       contagens e diagrama do fluxo PRISMA"
	@echo "  make relatorio    monta saidas/relatorio.md da revisão"
	@echo "  make analise      tudo, na ordem"
	@echo
	@echo "  make exemplo      roda a revisão de demonstração (dados SINTÉTICOS)"
	@echo "  make plugin       sincroniza o plugin em ../plugins/cienciometria com este motor"
	@echo "  make teste        executa os testes"
	@echo "  make limpar       apaga saídas e dados processados de uma revisão"

exige-revisao:
	@test -n "$(REVISAO)" || { echo "Informe a revisão: make <alvo> REVISAO=<slug>"; \
		echo; $(PY) -m cienciometria listar; exit 1; }

listar:
	@$(PY) -m cienciometria listar

nova:
	@test -n "$(SLUG)" || { echo "Informe o identificador: make nova SLUG=<slug> TITULO=\"...\""; exit 1; }
	$(PY) -m cienciometria nova $(SLUG) --titulo "$(TITULO)" --tema "$(TEMA)"

importar: exige-revisao
	$(PY) -m cienciometria importar $(ARGS)

dedup: exige-revisao
	$(PY) -m cienciometria dedup $(ARGS)

triagem: exige-revisao
	$(PY) -m cienciometria triagem $(ARGS)

kappa: exige-revisao
	$(PY) -m cienciometria kappa $(ARGS) $(if $(TRIAGEM),--triagem $(TRIAGEM),)

indicadores: exige-revisao
	$(PY) -m cienciometria indicadores $(ARGS)

redes: exige-revisao
	$(PY) -m cienciometria redes $(ARGS)

prisma: exige-revisao
	$(PY) -m cienciometria prisma $(ARGS)

relatorio: exige-revisao
	$(PY) -m cienciometria relatorio $(ARGS)

analise: exige-revisao
	$(PY) -m cienciometria analise $(ARGS)
	@echo "Relatório em revisoes/$(REVISAO)/saidas/relatorio.md"

exemplo:
	$(PY) testes/gerar_exemplo.py
	$(MAKE) analise REVISAO=exemplo-sintetico
	@echo
	@echo "AVISO: a revisão 'exemplo-sintetico' usa dados FABRICADOS. Não é resultado de pesquisa."

plugin:
	$(PY) ferramentas/sincronizar_plugin.py
	@$(PY) ferramentas/sincronizar_plugin.py --conferir

teste:
	$(PY) -m unittest discover -s testes -v

limpar: exige-revisao
	rm -rf revisoes/$(REVISAO)/saidas/* revisoes/$(REVISAO)/dados/processado/*
	@echo "saídas e dados processados de $(REVISAO) removidos (dados/bruto preservado)"

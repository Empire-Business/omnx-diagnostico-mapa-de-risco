---
name: omnx-diagnostico-mapa-de-risco
description: "Dá nota de 1 a 5 em cinco pilares (posicionamento, autoridade percebida, encaixe entre público e oferta, maturidade comercial, risco de reposicionamento) para saber se um perfil ou negócio está pronto para subir o preço ou lançar oferta de alto valor, a partir de uma pasta com os arquivos do cliente. Entrega relatório em Markdown e um único HTML com radar e tema claro e escuro. As notas são julgamento da IA, e nota alta exige prova nos arquivos. Use quando pedirem 'mapa de risco', 'diagnóstico estratégico do perfil', 'esse perfil está pronto para subir o preço?', 'análise de risco de reposicionamento', 'avalia a autoridade dessa marca'. Exige a pasta de insumos. Não use para brandbook ou relatório de Instagram (cami), montar a oferta ou definir preço (bento), analisar planilhas e dados (tales) nem escrever copy (rita)."
---

# Mapa de risco

Lê a pasta de arquivos de um cliente e dá nota, com evidência, em cinco pilares. Sai um relatório em Markdown e um HTML com radar, para mostrar ao cliente.

**A nota é um julgamento da IA a partir dos arquivos lidos.** Ela não mede resultado futuro e pode errar. O relatório diz isso. Repita à pessoa ao entregar. Nota alta exige prova: isso o script cobra.

## Como conversar

Quem usa pode não conhecer os termos. Se a pessoa chegar sem contexto, diga em duas linhas o que você faz e peça a pasta. Uma pergunta por vez. Palavra técnica vem com meia frase de explicação. Toda resposta termina com o próximo passo. A pessoa nunca precisa digitar comando.

## Passos

1. **Peça dois caminhos:** a pasta de insumos do cliente (só leitura) e a pasta onde salvar o resultado, fora da pasta de insumos. Sugira uma, mas quem escolhe é a pessoa. Se os insumos não existirem ou estiverem vazios, pare e diga isso em português simples.
2. **Leia tudo.** Abra cada arquivo da pasta. Anote o que não conseguiu ler (vídeo, áudio, arquivo protegido) e diga no resultado. Nada de nota baseada em arquivo não lido.
3. **Para cada pilar, evidência primeiro, nota depois.** Leia `references/pilares-e-regua.md` e separe cada achado em **prova** (dado ou documento verificável, como número em relatório, depoimento com resultado concreto, página de venda com preço) ou **indício** (afirmação sem comprovação, como "tenho muitos clientes", ou impressão sua). Toda evidência cita o arquivo de onde veio.
4. **Dê a nota de 1.0 a 5.0, de meia em meia.** Justifique em poucas frases. Atenção: no pilar 5, nota alta significa **risco baixo**. Se a pasta não tiver nada sobre um pilar, marque `nota: null` e diga o que falta: nunca dê nota média por falta de dado.
5. **Monte `dados.json` na pasta de saída**, no formato de `references/pilares-e-regua.md`.
6. **Gere os arquivos.** Rode, a partir da pasta deste `SKILL.md`:

   ```
   python3 scripts/gerar_mapa.py <saida>/dados.json --insumos <pasta-de-insumos> --saida <saida>
   ```

   O script calcula a nota geral e o status, confere as regras e escreve `mapa-de-risco.md` e `mapa-de-risco.html`. Se recusar, corrija o `dados.json`: **baixe a nota ou traga prova verdadeira.** Nunca troque indício por prova para passar.
7. **Entregue:** os dois caminhos, a nota geral, as três prioridades, o que você não conseguiu ler, e o aviso de que as notas são julgamento da IA. Ofereça abrir o HTML.

## Regras

- **Nota alta exige prova.** Nota 4 ou mais precisa de pelo menos duas provas com arquivo de origem. Sem isso, o script recusa.
- **Sem bajulação e sem drama.** Escreva o que os arquivos mostram.
- **Só o que está nos arquivos.** Não complete com o que você acha que o cliente provavelmente tem. Não pesquise o cliente na internet sem a pessoa pedir.
- **Dados de cliente ficam na máquina.** Não envie a pasta para serviço externo.
- **Insumos não são alterados.** A saída nunca fica dentro da pasta de insumos nem na pasta da skill.
- **Recomendação específica.** Cada uma diz o que fazer, em que formato e em que prazo.
- **Sem assinatura.** O relatório não leva nome de agente nem de autor.

## Outro sistema operacional

O único script é `scripts/gerar_mapa.py`, em Python 3 só com biblioteca padrão. Adapte o que for preciso e conte à pessoa o que realmente testou.

- **Python:** `python3` no macOS e Linux; `py -3` ou `python` no Windows. Sem Python, peça autorização para instalar pelo gerenciador oficial (Homebrew, winget, apt); sem ele não há como gerar o HTML nem garantir as contas, então diga isso e não faça o relatório à mão.
- **Instalar:** no Windows, copie esta pasta, sem o `install.sh`, para `%USERPROFILE%\.claude\skills\omnx-diagnostico-mapa-de-risco`. No Mac e no Linux, rode o `install.sh`.
- **Caminhos:** `~` é a pasta do usuário; no Windows é `%USERPROFILE%`. Caminho com espaço vai entre aspas.
- **Abrir o HTML para a pessoa:** `open` (macOS), `start ""` (Windows), `xdg-open` (Linux).

## Outra ferramenta (Codex e outras)

Esta skill foi feita e testada no Claude Code. **Não foi testada no Codex.** Se a pessoa pedir para instalar em outra ferramenta, a IA dela adapta na hora e conta o que realmente funcionou:

- **Onde pôr os arquivos:** confira na documentação atual da ferramenta. No Codex, a referência em 08/11/2026 era `~/.agents/skills/<name>`.
- **Caminhos:** `scripts/...` e `references/...` são relativos à pasta onde este `SKILL.md` ficou instalado.
- **Sem executar scripts:** a skill depende do script para calcular e validar. Diga à pessoa que não dá para gerar o mapa nessa ferramenta.

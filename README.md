# Mapa de risco

Guia visual: abra o `COMO-FUNCIONA.html` desta pasta (dois cliques; funciona sem internet).

Lê a pasta de arquivos de um cliente e dá nota, com evidência, em cinco pilares: posicionamento, autoridade percebida, encaixe entre público e oferta, maturidade comercial e risco de reposicionamento. Entrega um relatório em Markdown e um único HTML com radar e tema claro e escuro. **As notas são julgamento da IA a partir dos arquivos lidos, e nota alta exige prova.**

## Como instalar

**Direto do GitHub:** no Claude Code, diga: "Instale a skill a partir de https://github.com/Empire-Business/omnx-diagnostico-mapa-de-risco". Para atualizar, diga: "Atualize a skill a partir de https://github.com/Empire-Business/omnx-diagnostico-mapa-de-risco". A IA baixa e copia os arquivos.

Se você já baixou esta pasta:

1. Abra o Claude Code (aplicativo do Claude, aba **Code**, ambiente **Local**).
2. Escreva: **"Instale a skill omnx-diagnostico-mapa-de-risco a partir desta pasta: `<caminho desta pasta>`"**.
3. A IA copia a skill para o lugar certo. Você não digita comando nenhum e vê um aviso de que terminou.
4. Abra uma conversa nova e peça, por exemplo: **"Faz o mapa de risco deste cliente. Os arquivos estão nesta pasta."**.

### Instalar à mão

- **Mac ou Linux:** rode `bash install.sh` nesta pasta (dá para rodar de qualquer lugar, com o caminho entre aspas). A skill vai para `~/.claude/skills/omnx-diagnostico-mapa-de-risco`. Se editar algo aqui, rode de novo.
- **Windows:** copie esta pasta, sem o `install.sh`, para `%USERPROFILE%\.claude\skills\omnx-diagnostico-mapa-de-risco`. Ou peça para a IA fazer isso.

## Precisa de

Python 3 (gratuito), para calcular as notas e gerar o HTML. Se faltar, a IA avisa e só instala com a sua autorização.

## O que ela não faz

- Não mede resultado futuro: a nota é um julgamento da IA.
- Não dá nota alta sem prova nem nota a pilar sem dados.
- Não altera a pasta de arquivos do cliente.
- Brandbook é da Cami; oferta, do Bento; análise de planilhas, do Tales.

## Pedidos que funcionam

- "Faz o mapa de risco deste cliente. Os arquivos estão nesta pasta."
- "Esse perfil está pronto para subir o preço?"
- "Avalia o risco de reposicionamento dessa marca."
- "Refaz o diagnóstico agora que chegaram novos arquivos."

## Outro sistema operacional e outra ferramenta

As seções "Outro sistema operacional" e "Outra ferramenta (Codex e outras)" do `SKILL.md` dizem à IA o que adaptar. Feita e testada no Claude Code em macOS. **Não foi testada no Codex** nem no Windows e Linux: a IA da pessoa adapta ao instalar e conta o que funcionou.

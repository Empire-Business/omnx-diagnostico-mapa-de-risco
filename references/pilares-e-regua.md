# Pilares, régua e formato dos dados

## Régua

| Nota | Status | O que significa |
|---|---|---|
| 4.0 a 5.0 | APTO | Saudável, com prova. Não é gargalo. |
| 2.5 a 3.5 | ATENÇÃO | Lacuna real. Precisa de ação planejada. |
| 1.0 a 2.0 | CRÍTICO | Bloqueia. Tende a sabotar a oferta se ignorado. |

A nota geral é a média dos pilares avaliados, com uma casa decimal, e segue os mesmos limites (de 4.0 para cima, APTO; de 2.5 a 3.9, ATENÇÃO; abaixo de 2.5, CRÍTICO). Quando algum pilar fica sem nota, o relatório marca a nota geral como parcial.

**Nota alta exige prova.** O script recusa nota 4.0 ou mais com menos de duas evidências do tipo `prova`. Potencial não conta.

## Prova e indício

| Tipo | Exemplos |
|---|---|
| `prova` | Número em relatório de vendas; depoimento com resultado mensurável e identificável; página de vendas com preço público; funil documentado; print de pergunta de compra espontânea |
| `indicio` | "Tenho muitos clientes"; elogio genérico; bio que afirma autoridade sem mostrar; impressão sobre o tom dos posts |

Em dúvida, é indício.

## Os cinco pilares

### 1. Posicionamento (`posicionamento`)
Clareza do nicho, consistência da identidade, diferença real, coerência entre bio, posts e materiais.
Evidência forte: linguagem própria que se repete, linha editorial sem dispersão, documento de marca seguido nos posts.

### 2. Autoridade percebida (`autoridade`)
Profundidade demonstrada, casos documentados, credibilidade verificável.
Evidência forte: depoimentos com números concretos, método próprio nomeado e explicado, reconhecimento externo que dá para conferir.

### 3. Encaixe entre público e oferta (`encaixe`)
Quem segue é quem compra? Qualidade do engajamento: perguntas de compra contra elogios vazios.
Evidência forte: perguntas espontâneas de compra, pessoas descrevendo o problema que a oferta resolve, histórico de compra desse público.

### 4. Maturidade comercial (`maturidade`)
Estrutura ativa de vendas, frequência de oferta, receita que se repete ou que depende de golpes de sorte.
Evidência forte: funil documentado, preço público, sequência de nutrição ativa, histórico de vendas por período.

### 5. Risco de reposicionamento (`reposicionamento`)
O quanto o público reage mal a mudar tom, preço ou produto. **Nota inversa: nota alta significa risco baixo.**
Evidência forte: reação registrada a mudança passada, dependência forte de uma identidade específica, público comprador em faixa de preço distante da nova.

## Formato de `dados.json`

Os cinco pilares são obrigatórios. `tipo` é `prova` ou `indicio`. `fonte` é o caminho do arquivo, relativo à pasta de insumos (o script confere se ele existe). `onde` é opcional: página, linha ou trecho. Sem dados sobre um pilar, use `"nota": null` e `"falta"`.

```json
{
  "cliente": "Nome do cliente",
  "data": "2026-11-08",
  "resumo": "Uma frase sobre o estado atual, em tom neutro.",
  "veredito": "A frase que resume a situação e aponta o próximo passo mais urgente.",
  "nao_lidos": ["video-apresentacao.mp4"],
  "prioridades": ["Ação 1, a mais urgente", "Ação 2", "Ação 3"],
  "pilares": {
    "posicionamento": {
      "nota": 4.0,
      "justificativa": "O que os arquivos revelam, em poucas frases.",
      "evidencias": [
        {"tipo": "prova", "texto": "O que foi encontrado", "fonte": "posicionamento/brandbook.pdf", "onde": "p. 4"},
        {"tipo": "prova", "texto": "Outro achado", "fonte": "posts.md"},
        {"tipo": "indicio", "texto": "Algo sem comprovação", "fonte": "bio.txt"}
      ],
      "recomendacao": "O que fazer, em que formato e em que prazo."
    },
    "maturidade": {
      "nota": null,
      "falta": "Nenhum arquivo traz histórico de vendas ou funil.",
      "recomendacao": "Trazer o relatório de vendas dos últimos meses."
    }
  }
}
```

(No arquivo real, os cinco pilares estão presentes: `posicionamento`, `autoridade`, `encaixe`, `maturidade`, `reposicionamento`.)

## O que o script confere e recusa

- Pasta de insumos existe e tem arquivos.
- Pasta de saída fica fora dos insumos e fora da skill.
- Os cinco pilares estão presentes; notas entre 1.0 e 5.0, de meia em meia.
- Toda nota tem pelo menos uma evidência; nota de 4.0 para cima tem ao menos duas `prova`.
- Toda `fonte` existe dentro da pasta de insumos.
- Há de uma a cinco prioridades e pelo menos um pilar com nota.

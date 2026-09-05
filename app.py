from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def numero(valor, padrao=0.0):
    """Converte valores como 10,50 ou 10.50 para número."""
    if valor is None:
        return padrao

    try:
        texto = str(valor).strip()
        texto = texto.replace("R$", "").replace(" ", "")

        if "," in texto and "." in texto:
            # Exemplo: 1.234,56
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", ".")

        return float(texto)

    except (ValueError, TypeError):
        return padrao


@app.route("/", methods=["GET", "POST"])
def index():

    resultado = None

    if request.method == "POST":

        dados = request.form

        # =========================================================
        # PRODUÇÃO
        # =========================================================

        rendimento = max(
            numero(dados.get("rendimento")),
            0
        )

        quantidade_venda = max(
            numero(dados.get("quantidade_venda")),
            0
        )

        # =========================================================
        # EMBALAGENS
        # =========================================================

        custo_embalagem = max(
            numero(dados.get("custo_embalagem")),
            0
        )

        quantidade_embalagens = numero(
            dados.get("quantidade_embalagens"),
            quantidade_venda
        )

        if quantidade_embalagens <= 0:
            quantidade_embalagens = quantidade_venda

        # =========================================================
        # MÃO DE OBRA
        # =========================================================

        mao_obra = max(
            numero(dados.get("mao_obra")),
            0
        )

        # =========================================================
        # GASTOS EXTRAS
        # =========================================================

        gastos_extras = max(
            numero(dados.get("gastos_extras")),
            0
        )

        # =========================================================
        # PREÇO DE VENDA
        # =========================================================

        margem_desejada = numero(
            dados.get("margem_desejada"),
            50
        )

        if margem_desejada < 0:
            margem_desejada = 0

        if margem_desejada >= 100:
            margem_desejada = 99.9

        preco_venda = max(
            numero(dados.get("preco_venda")),
            0
        )

        # =========================================================
        # INGREDIENTES
        # =========================================================

        nomes = dados.getlist(
            "ingrediente_nome[]"
        )

        quantidades = dados.getlist(
            "ingrediente_quantidade[]"
        )

        unidades = dados.getlist(
            "ingrediente_unidade[]"
        )

        tamanhos = dados.getlist(
            "ingrediente_tamanho[]"
        )

        custos_pacotes = dados.getlist(
            "ingrediente_custo[]"
        )

        ingredientes = []

        custo_ingredientes = 0.0

        quantidade_linhas = max(
            len(nomes),
            len(quantidades),
            len(tamanhos),
            len(custos_pacotes)
        )

        for i in range(quantidade_linhas):

            nome = ""

            if i < len(nomes):
                nome = nomes[i].strip()

            qtd = 0

            if i < len(quantidades):
                qtd = numero(
                    quantidades[i]
                )

            unidade = "g"

            if i < len(unidades):
                unidade = unidades[i].strip()

            tamanho_pacote = 0

            if i < len(tamanhos):
                tamanho_pacote = numero(
                    tamanhos[i]
                )

            custo_pacote = 0

            if i < len(custos_pacotes):
                custo_pacote = numero(
                    custos_pacotes[i]
                )

            # Ignora linha totalmente vazia
            if (
                not nome
                and qtd <= 0
                and tamanho_pacote <= 0
                and custo_pacote <= 0
            ):
                continue

            # =====================================================
            # CÁLCULO DO CUSTO USADO
            # =====================================================

            custo_usado = 0.0

            if (
                qtd > 0
                and tamanho_pacote > 0
                and custo_pacote > 0
            ):

                custo_usado = (
                    qtd / tamanho_pacote
                ) * custo_pacote

            custo_ingredientes += custo_usado

            ingredientes.append(
                {
                    "nome": nome or "Ingrediente",
                    "quantidade": qtd,
                    "unidade": unidade,
                    "tamanho": tamanho_pacote,
                    "custo_pacote": custo_pacote,
                    "custo_usado": custo_usado
                }
            )

        # =========================================================
        # CUSTO DAS EMBALAGENS
        # =========================================================

        custo_embalagens_total = (
            custo_embalagem
            * quantidade_embalagens
        )

        # =========================================================
        # CUSTO TOTAL DA PRODUÇÃO
        # =========================================================

        custo_total = (
            custo_ingredientes
            + custo_embalagens_total
            + mao_obra
            + gastos_extras
        )

        # =========================================================
        # CUSTO POR DOCE
        # =========================================================

        if rendimento > 0:

            custo_por_doce = (
                custo_total / rendimento
            )

        else:

            custo_por_doce = 0.0

        # =========================================================
        # FATURAMENTO
        # =========================================================

        faturamento = (
            preco_venda
            * quantidade_venda
        )

        # =========================================================
        # CUSTO DOS DOCES VENDIDOS
        # =========================================================

        custo_das_unidades_vendidas = (
            custo_por_doce
            * quantidade_venda
        )

        # =========================================================
        # LUCRO
        # =========================================================

        lucro_total = (
            faturamento
            - custo_das_unidades_vendidas
        )

        lucro_por_doce = (
            preco_venda
            - custo_por_doce
        )

        # =========================================================
        # MARGEM REAL
        # =========================================================

        if faturamento > 0:

            margem_real = (
                lucro_total
                / faturamento
            ) * 100

        else:

            margem_real = 0.0

        # =========================================================
        # PREÇO SUGERIDO
        # =========================================================
        #
        # Exemplo:
        # Custo = R$ 1,00
        # Margem desejada = 50%
        #
        # Preço = 1 / (1 - 0,50)
        # Preço = R$ 2,00
        #
        # =========================================================

        if custo_por_doce > 0:

            preco_sugerido = (
                custo_por_doce
                / (
                    1
                    - (
                        margem_desejada
                        / 100
                    )
                )
            )

        else:

            preco_sugerido = 0.0

        # =========================================================
        # LUCRO COM PREÇO SUGERIDO
        # =========================================================

        lucro_sugerido_por_doce = (
            preco_sugerido
            - custo_por_doce
        )

        faturamento_sugerido = (
            preco_sugerido
            * quantidade_venda
        )

        lucro_sugerido_total = (
            faturamento_sugerido
            - custo_das_unidades_vendidas
        )

        # =========================================================
        # RESULTADO
        # =========================================================

        resultado = {

            "rendimento":
                rendimento,

            "quantidade_venda":
                quantidade_venda,

            "ingredientes":
                ingredientes,

            "custo_ingredientes":
                custo_ingredientes,

            "custo_embalagens":
                custo_embalagens_total,

            "mao_obra":
                mao_obra,

            "gastos_extras":
                gastos_extras,

            "custo_total":
                custo_total,

            "custo_por_doce":
                custo_por_doce,

            "preco_venda":
                preco_venda,

            "faturamento":
                faturamento,

            "lucro_total":
                lucro_total,

            "lucro_por_doce":
                lucro_por_doce,

            "margem_real":
                margem_real,

            "margem_desejada":
                margem_desejada,

            "preco_sugerido":
                preco_sugerido,

            "lucro_sugerido_por_doce":
                lucro_sugerido_por_doce,

            "faturamento_sugerido":
                faturamento_sugerido,

            "lucro_sugerido_total":
                lucro_sugerido_total
        }

    return render_template(
        "index.html",
        resultado=resultado
    )


# =============================================================
# TESTE DE FUNCIONAMENTO
# =============================================================

@app.route("/health")
def health():

    return jsonify(
        {
            "status": "ok",
            "aplicativo":
                "Calculadora de Doces 2.0"
        }
    )


# =============================================================
# EXECUÇÃO LOCAL
# =============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

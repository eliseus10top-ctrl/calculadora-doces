from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None

    if request.method == "POST":
        try:
            custo = float(request.form["custo"])
            quantidade = int(request.form["quantidade"])
            margem = float(request.form["margem"])

            if quantidade <= 0:
                raise ValueError

            # Custo de cada doce
            custo_unitario = custo / quantidade

            # Preço de venda com a margem desejada
            preco_unitario = custo_unitario * (1 + margem / 100)

            # Arredonda para 2 casas
            custo_unitario = round(custo_unitario, 2)
            preco_unitario = round(preco_unitario, 2)

            # Faturamento e lucro
            faturamento = preco_unitario * quantidade
            lucro = faturamento - custo

            resultado = {
                "custo": custo,
                "quantidade": quantidade,
                "margem": margem,
                "custo_unitario": custo_unitario,
                "preco_unitario": preco_unitario,
                "faturamento": round(faturamento, 2),
                "lucro": round(lucro, 2)
            }

        except (ValueError, TypeError):
            resultado = {
                "erro": "Digite valores válidos."
            }

    return render_template("index.html", resultado=resultado)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

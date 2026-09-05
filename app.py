from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None

    if request.method == "POST":
        try:
            # Recebe os valores do formulário
            custo = float(request.form.get("custo", 0))
            quantidade = int(request.form.get("quantidade", 0))
            preco = float(request.form.get("preco", 0))

            # Validação
            if custo < 0:
                raise ValueError("O custo não pode ser negativo.")

            if quantidade <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")

            if preco < 0:
                raise ValueError("O preço não pode ser negativo.")

            # Cálculos
            custo_unitario = custo / quantidade
            faturamento = preco * quantidade
            lucro = faturamento - custo

            # Margem de lucro sobre o faturamento
            if faturamento > 0:
                margem = (lucro / faturamento) * 100
            else:
                margem = 0

            # Resultado enviado para o index.html
            resultado = {
                "custo_unitario": custo_unitario,
                "faturamento": faturamento,
                "lucro": lucro,
                "margem": margem
            }

        except (ValueError, TypeError):
            resultado = None

    return render_template("index.html", resultado=resultado)


# Necessário para o Render/Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

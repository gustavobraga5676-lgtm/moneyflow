
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#050B1E")

        self.app = app

        titulo = ctk.CTkLabel(
            self,
            text="Dashboard Financeiro",
            font=("Arial", 35, "bold")
        )

        titulo.pack(pady=20)

        self.cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.cards_frame.pack(pady=10)

        self.saldo_card = self.create_card(
            "Saldo",
            "R$ 0.00",
            "#22C55E"
        )

        self.receita_card = self.create_card(
            "Receitas",
            "R$ 0.00",
            "#3B82F6"
        )

        self.despesa_card = self.create_card(
            "Despesas",
            "R$ 0.00",
            "#EF4444"
        )

        botoes_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        botoes_frame.pack(pady=20)

        receita_btn = ctk.CTkButton(
            botoes_frame,
            text="+ Receita",
            width=180,
            height=45,
            command=self.add_receita
        )

        receita_btn.pack(side="left", padx=10)

        despesa_btn = ctk.CTkButton(
            botoes_frame,
            text="- Despesa",
            width=180,
            height=45,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.add_despesa
        )

        despesa_btn.pack(side="left", padx=10)

        self.create_chart()
        self.update_dashboard()

    def create_card(self, titulo, valor, cor):

        card = ctk.CTkFrame(
            self.cards_frame,
            width=250,
            height=120,
            corner_radius=20
        )

        card.pack(side="left", padx=15)
        card.pack_propagate(False)

        titulo_label = ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 20, "bold")
        )

        titulo_label.pack(pady=(20, 5))

        valor_label = ctk.CTkLabel(
            card,
            text=valor,
            text_color=cor,
            font=("Arial", 28, "bold")
        )

        valor_label.pack()

        return valor_label

    def create_chart(self):

        frame = ctk.CTkFrame(
            self,
            corner_radius=20
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        fig = Figure(figsize=(6, 4), dpi=100)

        self.ax = fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(
            fig,
            master=frame
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        self.update_chart()

    def update_chart(self):

        self.ax.clear()

        self.app.cursor.execute(
            "SELECT tipo, valor FROM transacoes"
        )

        dados = self.app.cursor.fetchall()

        entradas = 0
        saidas = 0

        for tipo, valor in dados:

            if tipo == "Receita":
                entradas += valor
            else:
                saidas += valor

        valores = [entradas, saidas]

        if entradas == 0 and saidas == 0:
            valores = [1, 1]

        self.ax.pie(
            valores,
            labels=["Receitas", "Despesas"],
            autopct="%1.1f%%"
        )

        self.ax.set_title(
            "Distribuição Financeira"
        )

        self.canvas.draw()

    def add_receita(self):
        self.add_transaction("Receita")

    def add_despesa(self):
        self.add_transaction("Despesa")

    def add_transaction(self, tipo):

        valor = ctk.CTkInputDialog(
            text="Digite o valor:",
            title=tipo
        ).get_input()

        descricao = ctk.CTkInputDialog(
            text="Descrição:",
            title="Descrição"
        ).get_input()

        categoria = ctk.CTkInputDialog(
            text="Categoria:",
            title="Categoria"
        ).get_input()

        try:

            valor = float(valor)

            self.app.cursor.execute(
                """
                INSERT INTO transacoes(
                    tipo,
                    valor,
                    descricao,
                    categoria,
                    data
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    tipo,
                    valor,
                    descricao,
                    categoria,
                    str(datetime.now())
                )
            )

            self.app.conn.commit()

            self.update_dashboard()

            self.app.transactions_page.load_transactions()

            self.app.analytics_page.update_analytics()

            messagebox.showinfo(
                "Sucesso",
                "Transação adicionada"
            )

        except:

            messagebox.showerror(
                "Erro",
                "Digite um valor válido"
            )

    def update_dashboard(self):

        self.app.cursor.execute(
            "SELECT tipo, valor FROM transacoes"
        )

        dados = self.app.cursor.fetchall()

        entradas = 0
        saidas = 0

        for tipo, valor in dados:

            if tipo == "Receita":
                entradas += valor
            else:
                saidas += valor

        saldo = entradas - saidas

        self.saldo_card.configure(
            text=f"R$ {saldo:.2f}"
        )

        self.receita_card.configure(
            text=f"R$ {entradas:.2f}"
        )

        self.despesa_card.configure(
            text=f"R$ {saidas:.2f}"
        )

        self.update_chart()


class TransactionsPage(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#050B1E")

        self.app = app

        titulo = ctk.CTkLabel(
            self,
            text="Histórico",
            font=("Arial", 35, "bold")
        )

        titulo.pack(pady=20)

        self.search = ctk.CTkEntry(
            self,
            width=400,
            placeholder_text="Pesquisar..."
        )

        self.search.pack(pady=10)

        buscar_btn = ctk.CTkButton(
            self,
            text="Buscar",
            command=self.search_transaction
        )

        buscar_btn.pack(pady=10)

        excluir_btn = ctk.CTkButton(
            self,
            text="Excluir Última",
            fg_color="#DC2626",
            command=self.delete_last
        )

        excluir_btn.pack(pady=10)

        self.lista = ctk.CTkTextbox(
            self,
            width=1000,
            height=500
        )

        self.lista.pack(pady=20)

        self.load_transactions()

    def load_transactions(self):

        self.lista.delete("1.0", "end")

        self.app.cursor.execute(
            """
            SELECT tipo, valor, descricao,
            categoria, data
            FROM transacoes
            ORDER BY id DESC
            """
        )

        dados = self.app.cursor.fetchall()

        for linha in dados:

            texto = (
                f"{linha[0]} | "
                f"R$ {linha[1]:.2f} | "
                f"{linha[2]} | "
                f"{linha[3]} | "
                f"{linha[4]}\n"
            )

            self.lista.insert("end", texto)

    def search_transaction(self):

        termo = self.search.get()

        self.lista.delete("1.0", "end")

        self.app.cursor.execute(
            """
            SELECT tipo, valor, descricao,
            categoria, data
            FROM transacoes
            WHERE descricao LIKE ?
            """,
            (f"%{termo}%",)
        )

        dados = self.app.cursor.fetchall()

        for linha in dados:

            texto = (
                f"{linha[0]} | "
                f"R$ {linha[1]:.2f} | "
                f"{linha[2]} | "
                f"{linha[3]} | "
                f"{linha[4]}\n"
            )

            self.lista.insert("end", texto)

    def delete_last(self):

        self.app.cursor.execute(
            """
            DELETE FROM transacoes
            WHERE id = (
                SELECT MAX(id)
                FROM transacoes
            )
            """
        )

        self.app.conn.commit()

        self.load_transactions()

        self.app.dashboard_page.update_dashboard()

        self.app.analytics_page.update_analytics()

        messagebox.showinfo(
            "Sucesso",
            "Última transação removida"
        )


class AnalyticsPage(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#050B1E")

        self.app = app

        titulo = ctk.CTkLabel(
            self,
            text="Análise Financeira",
            font=("Arial", 35, "bold")
        )

        titulo.pack(pady=20)

        self.info = ctk.CTkTextbox(
            self,
            width=900,
            height=500
        )

        self.info.pack(pady=20)

        self.update_analytics()

    def update_analytics(self):

        self.info.delete("1.0", "end")

        self.app.cursor.execute(
            "SELECT tipo, valor FROM transacoes"
        )

        dados = self.app.cursor.fetchall()

        entradas = 0
        saidas = 0

        for tipo, valor in dados:

            if tipo == "Receita":
                entradas += valor
            else:
                saidas += valor

        saldo = entradas - saidas

        texto = (
            f"Entradas: R$ {entradas:.2f}\n\n"
            f"Despesas: R$ {saidas:.2f}\n\n"
            f"Saldo: R$ {saldo:.2f}\n\n"
        )

        if saldo > 0:
            texto += "Situação financeira positiva."
        else:
            texto += "Atenção aos gastos."

        self.info.insert("end", texto)


class ReportsPage(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#050B1E")

        self.app = app

        titulo = ctk.CTkLabel(
            self,
            text="Relatórios",
            font=("Arial", 35, "bold")
        )

        titulo.pack(pady=20)

        exportar_btn = ctk.CTkButton(
            self,
            text="Exportar TXT",
            command=self.exportar
        )

        exportar_btn.pack(pady=20)

    def exportar(self):

        self.app.cursor.execute(
            "SELECT * FROM transacoes"
        )

        dados = self.app.cursor.fetchall()

        with open(
            "relatorio.txt",
            "w",
            encoding="utf-8"
        ) as arquivo:

            arquivo.write(
                "=== MONEYFLOW ===\n\n"
            )

            for linha in dados:
                arquivo.write(str(linha) + "\n")

        messagebox.showinfo(
            "Exportado",
            "Relatório salvo"
        )


class GoalsPage(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#050B1E")

        titulo = ctk.CTkLabel(
            self,
            text="Metas Financeiras",
            font=("Arial", 35, "bold")
        )

        titulo.pack(pady=20)

        self.meta = ctk.CTkEntry(
            self,
            width=400,
            placeholder_text="Digite sua meta"
        )

        self.meta.pack(pady=20)

        salvar_btn = ctk.CTkButton(
            self,
            text="Salvar Meta",
            command=self.salvar_meta
        )

        salvar_btn.pack(pady=10)

    def salvar_meta(self):

        valor = self.meta.get()

        messagebox.showinfo(
            "Meta",
            f"Meta salva: {valor}"
        )


class MoneyFlowV4(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("MoneyFlow")

        self.state("zoomed")

        self.create_database()

        self.sidebar()

        self.container = ctk.CTkFrame(
            self,
            fg_color="#050B1E"
        )

        self.container.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.pages = {}

        dashboard = DashboardPage(
            self.container,
            self
        )

        transactions = TransactionsPage(
            self.container,
            self
        )

        analytics = AnalyticsPage(
            self.container,
            self
        )

        reports = ReportsPage(
            self.container,
            self
        )

        goals = GoalsPage(
            self.container,
            self
        )

        self.dashboard_page = dashboard
        self.transactions_page = transactions
        self.analytics_page = analytics

        self.pages["Dashboard"] = dashboard
        self.pages["Transactions"] = transactions
        self.pages["Analytics"] = analytics
        self.pages["Reports"] = reports
        self.pages["Goals"] = goals

        for page in self.pages.values():

            page.place(
                relwidth=1,
                relheight=1
            )

        self.show_page("Dashboard")

    def create_database(self):

        self.conn = sqlite3.connect(
            "moneyflow.db"
        )

        self.cursor = self.conn.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transacoes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                valor REAL,
                descricao TEXT,
                categoria TEXT,
                data TEXT
            )
            """
        )

        self.conn.commit()

    def sidebar(self):

        sidebar = ctk.CTkFrame(
            self,
            width=250,
            fg_color="#111827",
            corner_radius=0
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        logo = ctk.CTkLabel(
            sidebar,
            text="MoneyFlow",
            font=("Arial", 30, "bold")
        )

        logo.pack(pady=40)

        paginas = [
            ("Dashboard", "Dashboard"),
            ("Transações", "Transactions"),
            ("Análises", "Analytics"),
            ("Relatórios", "Reports"),
            ("Metas", "Goals")
        ]

        for texto, pagina in paginas:

            btn = ctk.CTkButton(
                sidebar,
                text=texto,
                height=45,
                command=lambda p=pagina:
                self.show_page(p)
            )

            btn.pack(
                fill="x",
                padx=15,
                pady=8
            )

        tema_btn = ctk.CTkButton(
            sidebar,
            text="Alternar Tema",
            command=self.toggle_theme
        )

        tema_btn.pack(
            fill="x",
            padx=15,
            pady=20
        )

    def toggle_theme(self):

        atual = ctk.get_appearance_mode()

        if atual == "Dark":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    def show_page(self, nome):

        self.pages[nome].tkraise()


if __name__ == "__main__":

    app = MoneyFlowV4()

    app.mainloop()
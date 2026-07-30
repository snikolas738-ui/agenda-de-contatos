"""
Agenda de Contatos.

Aplicação de linha de comando para gerenciar contatos (nome, telefone e
e-mail), com persistência em banco de dados SQLite. Permite adicionar,
listar, buscar, editar e remover contatos.

Autor: Nikolas Pereira Santos
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

NOME_BANCO = "contatos.db"


@dataclass
class Contato:
    """Representa um contato da agenda."""

    id: int | None
    nome: str
    telefone: str
    email: str

    def __str__(self) -> str:
        return f"[{self.id}] {self.nome} | Tel: {self.telefone} | E-mail: {self.email}"


class AgendaContatos:
    """Gerencia a persistência dos contatos em um banco de dados SQLite."""

    def __init__(self, caminho_banco: str = NOME_BANCO) -> None:
        self.caminho_banco = Path(caminho_banco)
        self._criar_tabela()

    def _conectar(self) -> sqlite3.Connection:
        return sqlite3.connect(self.caminho_banco)

    def _criar_tabela(self) -> None:
        with self._conectar() as conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS contatos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    email TEXT NOT NULL
                )
                """
            )

    def adicionar(self, nome: str, telefone: str, email: str) -> Contato:
        """Adiciona um novo contato e retorna o contato criado (com id)."""
        with self._conectar() as conexao:
            cursor = conexao.execute(
                "INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)",
                (nome, telefone, email),
            )
            return Contato(id=cursor.lastrowid, nome=nome, telefone=telefone, email=email)

    def listar(self) -> list[Contato]:
        """Retorna todos os contatos cadastrados, ordenados por nome."""
        with self._conectar() as conexao:
            linhas = conexao.execute(
                "SELECT id, nome, telefone, email FROM contatos ORDER BY nome"
            ).fetchall()
        return [Contato(*linha) for linha in linhas]

    def buscar(self, termo: str) -> list[Contato]:
        """Busca contatos cujo nome contenha o termo informado (case-insensitive)."""
        with self._conectar() as conexao:
            linhas = conexao.execute(
                "SELECT id, nome, telefone, email FROM contatos "
                "WHERE nome LIKE ? ORDER BY nome",
                (f"%{termo}%",),
            ).fetchall()
        return [Contato(*linha) for linha in linhas]

    def editar(self, id_contato: int, nome: str, telefone: str, email: str) -> bool:
        """Atualiza um contato existente. Retorna True se algo foi alterado."""
        with self._conectar() as conexao:
            cursor = conexao.execute(
                "UPDATE contatos SET nome = ?, telefone = ?, email = ? WHERE id = ?",
                (nome, telefone, email, id_contato),
            )
            return cursor.rowcount > 0

    def remover(self, id_contato: int) -> bool:
        """Remove um contato pelo id. Retorna True se algo foi removido."""
        with self._conectar() as conexao:
            cursor = conexao.execute(
                "DELETE FROM contatos WHERE id = ?", (id_contato,)
            )
            return cursor.rowcount > 0


def _ler_texto_obrigatorio(mensagem: str) -> str:
    """Lê uma string do usuário, repetindo até que não esteja vazia."""
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Este campo não pode ficar vazio.")


def _ler_id(mensagem: str) -> int | None:
    """Lê um id numérico do usuário. Retorna None se a entrada for inválida."""
    entrada = input(mensagem).strip()
    if entrada.isdigit():
        return int(entrada)
    print("Id inválido. Digite apenas números.")
    return None


def exibir_menu() -> str:
    print("\n" + "=" * 40)
    print("          AGENDA DE CONTATOS")
    print("=" * 40)
    print("1. Adicionar contato")
    print("2. Listar contatos")
    print("3. Buscar contato por nome")
    print("4. Editar contato")
    print("5. Remover contato")
    print("0. Sair")
    return input("Escolha uma opção: ").strip()


def imprimir_contatos(contatos: list[Contato]) -> None:
    if not contatos:
        print("Nenhum contato encontrado.")
        return
    for contato in contatos:
        print(contato)


def main() -> None:
    agenda = AgendaContatos()

    while True:
        opcao = exibir_menu()

        if opcao == "1":
            nome = _ler_texto_obrigatorio("Nome: ")
            telefone = _ler_texto_obrigatorio("Telefone: ")
            email = _ler_texto_obrigatorio("E-mail: ")
            contato = agenda.adicionar(nome, telefone, email)
            print(f"Contato adicionado com sucesso: {contato}")

        elif opcao == "2":
            imprimir_contatos(agenda.listar())

        elif opcao == "3":
            termo = _ler_texto_obrigatorio("Digite o nome (ou parte dele): ")
            imprimir_contatos(agenda.buscar(termo))

        elif opcao == "4":
            id_contato = _ler_id("Id do contato a editar: ")
            if id_contato is None:
                continue
            nome = _ler_texto_obrigatorio("Novo nome: ")
            telefone = _ler_texto_obrigatorio("Novo telefone: ")
            email = _ler_texto_obrigatorio("Novo e-mail: ")
            if agenda.editar(id_contato, nome, telefone, email):
                print("Contato atualizado com sucesso.")
            else:
                print("Nenhum contato encontrado com esse id.")

        elif opcao == "5":
            id_contato = _ler_id("Id do contato a remover: ")
            if id_contato is None:
                continue
            if agenda.remover(id_contato):
                print("Contato removido com sucesso.")
            else:
                print("Nenhum contato encontrado com esse id.")

        elif opcao == "0":
            print("Até logo!")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()

from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func

from config import Config
from extensions import db, login_manager
from models import User, Board, Column, Membership, Card, JoinNotification
from form import LoginForm, RegisterForm, EditCardForm
from services import login_service
from services.register_service import register_user


def init_app(app):
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        db.create_all()


def create_app():
    app = Flask(__name__)
    init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            valid, message, user_id = login_service.login_service(username, password)
            if valid:
                user = User.query.get(user_id)
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash(message, 'error')
                return redirect(url_for('login'))

        return render_template('login.html', form=form)

    @app.route('/log_off')
    def log_out():
        logout_user()
        flash('Você foi desconectado com sucesso.', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    def dashboard():
        return render_template("dashboard.html")

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            result = register_user(form.username.data, form.password.data)
            if "error" in result:
                flash(result["error"], "error")
                return redirect(url_for('register'))
            else:
                flash(result["success"], "success")
                login_user(result["user"])
                return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/create_board', methods=['GET', 'POST'])
    @login_required
    def create_board():
        if request.method == 'POST':
            board_name = request.form.get('name')

            if not board_name:
                flash('Nome do quadro é necessário.', 'danger')
                return redirect(url_for('create_board'))

            new_board = Board(name=board_name, creator_id=current_user.id)
            db.session.add(new_board)
            db.session.commit()

            default_column = Column(name='Backlog', board_id=new_board.id)
            db.session.add(default_column)
            db.session.commit()

            default_card = Card(
                title='Test Card',
                description='Card de teste.',
                status=default_column.name,
                board_id=new_board.id,
                column_id=default_column.id,
                creator_id=current_user.id,
                assigned_to_id=current_user.id
            )
            db.session.add(default_card)
            db.session.commit()

            flash('Quadro criado com sucesso!', 'success')
            return redirect(url_for('view_board', board_id=new_board.id))

        return render_template('create_board.html')

    @app.route('/board/<int:board_id>')
    @login_required
    def view_board(board_id):
        board = Board.query.get_or_404(board_id)

        if current_user not in board.members and current_user != board.creator:
            flash('Você não tem permissão para visualizar este quadro.', 'danger')
            return redirect(url_for('dashboard'))

        columns = Column.query.filter_by(board_id=board_id).all()
        cards = Card.query.filter_by(board_id=board_id).all()

        status_to_column = {column.name: column for column in columns}

        column_id_to_cards = {column.id: [] for column in columns}

        for card in cards:
            column = status_to_column.get(card.status)
            if column:
                column_id_to_cards[column.id].append({
                    "id": card.id,
                    "title": card.title,
                    "description": card.description,
                    "assigned_to": card.assignee.username if card.assignee else None,
                })

        users = User.query.all()

        return render_template('view_board.html', board=board, columns=columns, column_id_to_cards=column_id_to_cards, users=users)

    @app.route('/list_boards')
    @login_required
    def list_boards():
        boards_with_user = Board.query.join(Membership).filter(
            Membership.user_id == current_user.id
        ).all()

        user_created_boards = Board.query.filter_by(creator_id=current_user.id).all()

        boards_user_is_involved = set(boards_with_user) | set(user_created_boards)

        all_boards = Board.query.all()

        other_boards = [board for board in all_boards if board not in boards_user_is_involved]

        return render_template('list_boards.html', my_boards=boards_with_user, other_boards=other_boards)

    @app.route('/join_board/<int:board_id>', methods=['POST'])
    @login_required
    def join_board(board_id):
        user_id = current_user.id

        board = Board.query.get_or_404(board_id)

        existing_membership = Membership.query.filter_by(user_id=user_id, board_id=board_id).first()
        if existing_membership:
            flash('Você já é um membro deste quadro.', 'info')
            return redirect(url_for('view_board', board_id=board_id))

        if user_id == board.creator_id:
            flash('Você não pode se juntar ao seu próprio quadro.', 'danger')
            return redirect(url_for('view_board', board_id=board_id))

        join_notification = JoinNotification(
            user_id=user_id,
            board_id=board_id,
            board_owner_id=board.creator_id,
            created_at=func.now(),
            approved=False,
            refused=False
        )

        db.session.add(join_notification)
        db.session.commit()

        flash('Solicitação de adesão enviada com sucesso!', 'success')
        return redirect(url_for('view_board', board_id=board_id))

    @app.route('/edit_board_name/<int:board_id>', methods=['POST'])
    @login_required
    def edit_board_name(board_id):
        board = Board.query.get_or_404(board_id)

        if current_user not in board.members and current_user != board.creator:
            flash('Você não tem permissão para editar o nome do quadro.', 'danger')
            return redirect(url_for('view_board', board_id=board.id))

        new_name = request.form.get('name')

        if new_name:
            board.name = new_name
            db.session.commit()
            flash('Nome do quadro atualizado com sucesso!', 'success')
        else:
            flash('Nome do quadro não pode ser vazio.', 'danger')

        return redirect(url_for('view_board', board_id=board.id))

    @app.route('/add_column/<int:board_id>', methods=['POST'])
    @login_required
    def add_column(board_id):
        board = Board.query.get_or_404(board_id)

        if current_user not in board.members and current_user != board.creator:
            flash('Você não tem permissão para gerenciar colunas.', 'danger')
            return redirect(url_for('view_board', board_id=board.id))

        column_name = request.form.get('column_name')
        if not column_name:
            flash('Nome da coluna não pode ser vazio.', 'danger')
        else:
            column = Column(name=column_name, board=board)
            db.session.add(column)
            db.session.commit()
            flash('Coluna adicionada com sucesso!', 'success')

        return redirect(url_for('view_board', board_id=board.id))

    @app.route('/edit_column/<int:column_id>', methods=['POST'])
    @login_required
    def edit_column(column_id):
        new_name = request.form.get('new_name')
        column = Column.query.get_or_404(column_id)
        board_id = column.board_id

        if not new_name:
            flash("Nome da coluna não pode ser vazio!", "danger")
        else:
            column.name = new_name
            db.session.commit()
            flash("Nome da coluna atualizado com sucesso!", "success")

        return redirect(url_for('view_board', board_id=board_id))

    @app.route('/delete_column/<int:board_id>/<int:column_id>', methods=['POST'])
    @login_required
    def delete_column(board_id, column_id):
        column = Column.query.get_or_404(column_id)
        board = column.board

        if current_user not in board.members and current_user != board.creator:
            flash('Você não tem permissão para deletar colunas.', 'danger')
        else:
            db.session.delete(column)
            db.session.commit()
            flash('Coluna deletada com sucesso!', 'success')

        return redirect(url_for('view_board', board_id=board_id))

    @app.route('/create_card', methods=['GET', 'POST'])
    @login_required
    def create_card():
        board_id = request.form.get('board_id')
        title = request.form.get('title')
        description = request.form.get('description')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        assigned_to_id = request.form.get('assigned_to')
        column_id = request.form.get('column_id')

        column = Column.query.get_or_404(column_id)

        if not board_id:
            flash('Board ID é necessário.', 'danger')
            return redirect(url_for('dashboard'))

        board = Board.query.get_or_404(board_id)

        if current_user not in board.members and current_user != board.creator:
            flash('Você não tem permissão para criar cards nesse board.', 'danger')
            return redirect(url_for('view_board', board_id=board.id))

        try:
            new_card = Card(
                title=title,
                description=description,
                start_time=datetime.strptime(start_time, '%Y-%m-%dT%H:%M') if start_time else None,
                end_time=datetime.strptime(end_time, '%Y-%m-%dT%H:%M') if end_time else None,
                assigned_to_id=int(assigned_to_id) if assigned_to_id else None,
                board_id=board_id,
                creator_id=current_user.id,
                column_id=column_id,
                status=column.name
            )
        except ValueError as e:
            flash(f'Formato de data incorreto. Erro: {e}', 'danger')
            return redirect(url_for('view_board', board_id=board.id))

        db.session.add(new_card)
        db.session.commit()

        flash('Card criado com sucesso!', 'success')

        return redirect(url_for('view_board', board_id=board_id))

    @app.route('/update_card/<int:card_id>', methods=['GET', 'POST'])
    @login_required
    def update_card(card_id):
        card = Card.query.get_or_404(card_id)
        columns = Column.query.filter_by(board_id=card.board_id).all()

        form = EditCardForm(obj=card)
        form.column_id.choices = [(column.id, column.name) for column in columns]

        if request.method == 'POST':
            if form.validate_on_submit():
                if current_user not in card.board.members and current_user != card.board.creator:
                    flash('Você não tem permissão para editar cards nesse board.', 'danger')
                    return redirect(url_for('view_board', board_id=card.board_id))

                selected_column_id = form.column_id.data
                selected_column = Column.query.get(selected_column_id)
                card.status = selected_column.name if selected_column else None

                card.title = form.title.data
                card.description = form.description.data
                card.start_time = form.start_time.data
                card.end_time = form.end_time.data
                card.column_id = form.column_id.data

                db.session.commit()

                flash('Card atualizado com sucesso!', 'success')
                return redirect(url_for('view_board', board_id=card.board_id))

        return render_template('edit_card.html', form=form)

    @app.route('/card/<int:card_id>', methods=['GET', 'POST'])
    @login_required
    def card_details(card_id):
        card = Card.query.get_or_404(card_id)

        if current_user not in card.board.members and current_user != card.board.creator:
            flash('Você não tem permissão para visualizar os detalhes deste card.', 'danger')
            return redirect(url_for('view_board', board_id=card.board_id))

        return render_template('card.html', card=card)

    @app.route('/delete_card/<int:card_id>', methods=['POST'])
    @login_required
    def delete_card(card_id):
        card = Card.query.get_or_404(card_id)
        board = card.board

        if current_user not in board.members and current_user != board.creator:
            flash('Você não tem permissão para deletar este card.', 'danger')
            return redirect(url_for('view_board', board_id=card.board_id))

        db.session.delete(card)
        db.session.commit()
        flash('Card deletado com sucesso!', 'success')

        return redirect(url_for('view_board', board_id=card.board_id))

    @app.route('/api/boards/<int:board_id>/cards', methods=['GET'])
    @login_required
    def list_cards(board_id):

        board = Board.query.get_or_404(board_id)

        if current_user not in board.members and current_user != board.creator:
            flash('Você não tem permissão para visualizar os cards deste quadro.', 'danger')
            return jsonify({"error": "Access forbidden"}), 403

        cards = Card.query.filter_by(board_id=board_id).all()

        card_list = [
            {
                "id": card.id,
                "title": card.title,
                "description": card.description,
                "start_time": card.start_time.isoformat() if card.start_time else None,
                "end_time": card.end_time.isoformat() if card.end_time else None,
                "status": card.status,
                "assignee": card.assignee.username if card.assignee else None
            }
            for card in cards
        ]
        return card_list

    def get_board_by_id(board_id):
        board = Board.query.get(board_id)
        if board is None:
            return None
        return board

    @app.route('/api/boards/<int:board_id>/columns', methods=['GET'])
    def get_columns(board_id):
        board = get_board_by_id(board_id)
        columns = [{'id': column.id, 'name': column.name} for column in board.columns]
        return jsonify(columns)

    @app.route('/api/move_card', methods=['POST'])
    @login_required
    def move_card():
        data = request.form
        card_id = data.get('card_id')
        target_column_id = data.get('target_column_id')

        card = Card.query.get(card_id)
        if card is None:
            flash('Card not found.', 'danger')
            return redirect(url_for('view_board', board_id=card.board_id))

        column = Column.query.get(target_column_id)
        if column is None:
            flash('Column not found.', 'danger')
            return redirect(url_for('view_board', board_id=card.board_id))

        card.column_id = target_column_id
        card.status = column.name

        db.session.commit()
        flash('Card moved successfully.', 'success')
        return redirect(url_for('view_board', board_id=card.board_id))

    @app.route('/api/boards/<int:board_id>/card-titles', methods=['GET'])
    @login_required
    def list_card_titles(board_id):
        board = Board.query.get_or_404(board_id)

        if current_user not in board.members and current_user != board.creator:
            flash('Você não tem permissão para visualizar os títulos dos cards deste quadro.', 'danger')
            return jsonify({"error": "Access forbidden"}), 403

        cards = Card.query.filter_by(board_id=board_id).all()

        card_titles = [
            {
                "id": card.id,
                "title": card.title
            }
            for card in cards
        ]
        return card_titles

    @app.route('/requests')
    @login_required
    def requests_page():
        boards_with_requests = JoinNotification.query.join(Board).filter(
            JoinNotification.board_owner_id == current_user.id,
            JoinNotification.approved.is_(False),
            JoinNotification.refused.is_(False)
        ).all()

        user_requests = JoinNotification.query.filter_by(
            user_id=current_user.id,
            approved=False,
            refused=False
        ).all()

        completed_requests = JoinNotification.query.filter(
            JoinNotification.user_id == current_user.id,
            JoinNotification.approved.is_(True) | JoinNotification.refused.is_(True)
        ).all()

        return render_template(
            'requests.html',
            boards_with_requests=boards_with_requests,
            user_requests=user_requests,
            completed_requests=completed_requests
        )

    @app.route('/approve_request/<int:notification_id>', methods=['POST'])
    @login_required
    def approve_request(notification_id):
        notification = JoinNotification.query.get_or_404(notification_id)

        if notification.board_owner_id != current_user.id:
            flash('Você não tem permissão para aprovar esta solicitação.', 'danger')
            return redirect(url_for('requests_page'))

        notification.approved = True
        notification.approved_at = func.now()

        board = notification.board
        user = notification.user

        existing_membership = Membership.query.filter_by(user_id=user.id, board_id=board.id).first()
        if not existing_membership:
            new_membership = Membership(user_id=user.id, board_id=board.id, approved=True, role='member')
            db.session.add(new_membership)

        db.session.commit()
        flash('Solicitação aprovada com sucesso!', 'success')
        return redirect(url_for('requests_page'))

    @app.route('/reject_request/<int:notification_id>', methods=['POST'])
    @login_required
    def reject_request(notification_id):
        notification = JoinNotification.query.get_or_404(notification_id)

        if notification.board_owner_id != current_user.id:
            flash('Você não tem permissão para recusar esta solicitação.', 'danger')
            return redirect(url_for('requests_page'))

        notification.refused = True
        db.session.commit()
        flash('Solicitação recusada com sucesso!', 'danger')
        return redirect(url_for('requests_page'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Book

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Создание таблиц
with app.app_context():
    db.create_all()

# Данные для выпадающих списков
GENRES = ['Фантастика', 'Фэнтези', 'Детектив', 'Роман', 'Научная литература', 
          'Биография', 'Исторический', 'Ужасы', 'Триллер', 'Приключения']

STATUSES = [
    ('planned', 'В планах'),
    ('reading', 'Читаю'),
    ('completed', 'Прочитано')
]

RATINGS = [(i, str(i)) for i in range(1, 6)]

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    # Фильтрация и поиск
    search_query = request.args.get('search', '')
    genre_filter = request.args.get('genre', '')
    status_filter = request.args.get('status', '')
    
    # Базовый запрос
    books_query = Book.query
    
    if search_query:
        books_query = books_query.filter(
            (Book.title.ilike(f'%{search_query}%')) | 
            (Book.author.ilike(f'%{search_query}%'))
        )
    
    if genre_filter:
        books_query = books_query.filter(Book.genre == genre_filter)
    
    if status_filter:
        books_query = books_query.filter(Book.status == status_filter)
    
    # Сортировка по дате добавления (новые сначала)
    books_query = books_query.order_by(Book.created_at.desc())
    
    # Пагинация
    books = books_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('index.html', 
                         books=books,
                         genres=GENRES,
                         statuses=STATUSES,
                         search_query=search_query,
                         genre_filter=genre_filter,
                         status_filter=status_filter)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    # Заглушка - будет реализована в другой ветке
    if request.method == 'POST':
        flash('Функция добавления книги будет реализована позже', 'info')
        return redirect(url_for('index'))
    return render_template('add_book.html', 
                         genres=GENRES, 
                         statuses=STATUSES, 
                         ratings=RATINGS)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book, statuses=STATUSES)

@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        try:
            book.title = request.form['title']
            book.author = request.form['author']
            book.year = int(request.form['year'])
            book.genre = request.form['genre']
            book.status = request.form['status']
            book.rating = int(request.form['rating']) if request.form['rating'] else None
            
            db.session.commit()
            flash('Книга успешно обновлена!', 'success')
            return redirect(url_for('book_detail', book_id=book.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении книги: {str(e)}', 'danger')
    
    return render_template('edit_book.html', 
                         book=book,
                         genres=GENRES, 
                         statuses=STATUSES, 
                         ratings=RATINGS)

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Книга успешно удалена!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении книги: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
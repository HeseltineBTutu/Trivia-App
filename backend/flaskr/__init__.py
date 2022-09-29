import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Headers',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        '''
        End point to get all available categories

        '''
        categories = Category.query.order_by(Category.type).all()
        if len(categories) == 0:
            abort(404)

        return jsonify({"categories": {
                       category.id: category.type for category in categories}})

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.type).all()
        paginated_questions = paginate_questions(request, questions)

        if len(paginated_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'totalQuestions': len(questions),
            'categories': {
                category.id: category.type for category in categories},
            'currentCategory': None


        })

    @app.route('/questions/<int:question_id>', methods=(['DELETE']))
    def delete_question(question_id):
        '''
        Endpoint to DELETE question using a question ID.
        '''

        question = Question.query.get(question_id)

        if not question:
            abort(404)

        try:
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except BaseException:

            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        try:

            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty)
            print("before", len(Question.query.all()))

            question.insert()

            print("after", len(Question.question.all()))
            selection = Question.query.order_by(Question.id).all()

            current_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except BaseException:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        searchTerm = request.json.get('searchTerm')
        try:

            if searchTerm is None:
                abort(404)
            else:
                questions = Question.query.filter(
                    Question.question.ilike(f'%{searchTerm}%')).all()
                formatted_questions = [question.format()
                                       for question in questions]

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'totalQuestions': len(questions),
                'currentCategory': None
            })
        except BaseException:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()
            formated_questions = [question.format() for question in questions]

            if category_id is None:
                abort(404)

            return jsonify({
                'success': True,
                'questions': formated_questions,
                'totalQuestions': len(questions),
                'currentCategory': category_id

            })
        except BaseException:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_question_to_play():

        body = request.get_json()
        category = body.get('quiz_category')
        previous_questions = body.get('previous_question')
        category_id = category['id']

        try:

            if category_id == 0:
                new_quizzes = Question.query.filter(
                    Question.id.notin_(previous_questions),
                    Question.category == category_id).all()
                formatted_quiz = []

                for question in new_quizzes:
                    formatted_quiz.append(question.format())
                else:
                    new_quizzes = Question.query.filter(
                        Question.id.notin_(previous_questions),
                        Question.category == category_id).all()

                    formated_quiz = []

                    for question in new_quizzes:

                        formated_quiz.append(question.format())

                        current_question = None
                        if formatted_quiz:
                            current_question = random.choice(formatted_quiz)

            return jsonify({
                'success': True,
                'question': current_question
            })
        except BaseException:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected error
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return ({
            "success": False,
            "error": 400,
            "message": "bad request"
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        })

    @app.errorhandler(405)
    def not_found(error):
        return ({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        })

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unproccessable"
        })

    @app.errorhandler(500)
    def internal_server_error(error):
        return ({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        })
    return app

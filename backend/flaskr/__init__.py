from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, list):
    # get page
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    # format the list
    formatted_list = [row.format() for row in list]

    # filter list
    return formatted_list[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    if test_config is None:
        setup_db(app)
    CORS(app)

    # CORS configuration using after_request
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,PUT,DELETE'
        )
        return response

    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    # get the list of categories
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            # return 404
            abort(404)
        else:
            # return 200
            return jsonify({
                'categories': {
                    str(category.id): category.type for category in categories
                }
            })

    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of
    the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    # get the list of questions, paginated
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # get categories list
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)
        else:
            # take the first category as current
            current_category = categories[0].type

            # get questions
            list = Question.query.order_by(Question.id).all()

            # paginate questions
            current_questions = paginate_questions(request, list)

            if len(current_questions) == 0:
                # return 404
                abort(404)
            else:
                # return 200
                return jsonify({
                    'questions': current_questions,
                    'categories': {
                        str(row.id): row.type for row in categories
                    },
                    'currentCategory': current_category,
                    'totalQuestions': len(list)
                })

    """
    Create a GET endpoint to get questions based on category.
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    # get the list of questions by category
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        # get the category
        category = Category.query.filter(
            Category.id == category_id).one_or_none()

        if category is None:
            abort(404, 'Category not found.')

        # get the questions
        base_query = Question.query.filter(Question.category == category_id)

        # get questions from db
        list = base_query.all()

        # paginate questions
        current_questions = paginate_questions(request, list)

        if len(current_questions) == 0:
            # return 404
            abort(404)
        else:
            # return 200
            return jsonify({
                'questions': current_questions,
                'totalQuestions': len(list),
                "currentCategory": category.type
            })

    """
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you
    refresh the page.
    """
    # delete a single question
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        try:
            # get the question by id
            question = Question.query.filter(
                Question.id == question_id
            ).one_or_none()

            # returns formatted result
            if question is None:
                # not found
                abort(404)
            else:
                # delete question
                question.delete()

                # success
                return jsonify({
                    'deleted': question.id
                })
        except Exception as ex:
            # internal server error
            print(f'Error deleting question: {ex}')
            abort(500, 'Error deleting the question.')

    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    """
    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    # create a new question or search
    @app.route('/questions', methods=['POST'])
    def create_or_search_question():
        # get body
        body = request.get_json()
        if body is None:
            abort(400, 'Body is empty.')

        # get body parameters
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', 1)
        search = body.get('searchTerm', None)

        if search is not None:
            # search questions
            list = Question.query.filter(
                Question.question.ilike(f'%{search}%')
            ).order_by(
                Question.id
            ).all()

            # paginate questions
            current_questions = paginate_questions(request, list)

            category = Category.query.order_by(Category.id).first()

            # return found results
            return jsonify({
                'questions': current_questions,
                'totalQuestions': len(list),
                'currentCategory': category.type
            }), 200
        elif new_question is not None and new_answer is not None:
            # get category id
            category = Category.query.filter_by(id=new_category).one_or_none()

            if category is None:
                abort(400, 'Category is not correct.')

            # create question
            question = Question(
                question=new_question,
                answer=new_answer,
                category=category.id,
                difficulty=new_difficulty
            )
            question.insert()

            # created
            return jsonify({
                'created': question.id
            }), 201
        else:
            abort(422)

    """
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        # get body parameters
        body = request.get_json()
        quiz_category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)

        # check body validity
        if quiz_category is None or previous_questions is None:
            abort(
                400,
                'Both "quiz_category" and "previous_questions" are required.'
            )

        # get category id
        category_id = quiz_category.get('id')

        # base query
        base_query = Question.query

        # filter by category
        if category_id != 0:
            base_query = base_query.filter_by(category=category_id)

        # get questions from db
        questions = base_query.all()

        # filter out previous questions
        if previous_questions is not None:
            questions = [
                q for q in questions if q.id not in previous_questions]

        # if no available questions return empty response
        if not questions:
            return jsonify({
                'question': None
            }), 200
        else:
            # select a random question
            random_question = random.choice(questions)

            # return random question
            return jsonify({
                'question': random_question.format()
            }), 200

    """
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": f"Bad request {error}"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": f"Not found. {error}"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": f"Method not allowed. {error}"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": f"Unprocessable. {error}"
        }), 500

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": f"Internal server error. {error}"
        }), 500

    return app

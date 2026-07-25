@auth_bp.route('/login-page')
def login_page():
    """Login sayfasını render et"""
    try:
        return render_template('login.html')
    except Exception as e:
        return jsonify({"error": f"Login template error: {str(e)}"}), 404
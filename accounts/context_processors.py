def user_badge(request):
    """
    Injecte le badge de l'utilisateur courant dans tous les templates.
    Permet d'afficher le badge dans la navbar, messages, etc.
    """
    if request.user.is_authenticated and request.user.afficher_badge:
        return {
            'user_badge':        request.user.badge,
            'user_badge_icone':  request.user.badge.icone,
            'user_est_certifie': True,
        }
    return {
        'user_badge':        None,
        'user_badge_icone':  '',
        'user_est_certifie': False,
    }

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from accounts.models import User
from marketplace.models import Article


@login_required
def liste_conversations(request):
    conversations = list(request.user.conversations.prefetch_related(
        'participants', 'participants__badge'
    ).order_by('-updated_at'))

    result = []
    for conv in conversations:
        autre = conv.autre_participant(request.user)
        if autre is None:
            continue  # ignorer les conversations sans interlocuteur valide
        conv.nb_non_lus_user = conv.nb_non_lus(request.user)
        conv.autre_user      = autre
        conv.dernier         = conv.dernier_message()
        result.append(conv)

    return render(request, 'messaging/liste.html', {'conversations': result})


@login_required
def conversation(request, conv_pk):
    conv = get_object_or_404(
        Conversation.objects.prefetch_related('participants', 'participants__badge'),
        pk=conv_pk,
        participants=request.user
    )

    conv.messages_conv.filter(is_read=False).exclude(
        expediteur=request.user
    ).update(is_read=True)

    msgs = conv.messages_conv.select_related('expediteur', 'expediteur__badge').all()

    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        if contenu:
            Message.objects.create(conversation=conv, expediteur=request.user, contenu=contenu)
            conv.save()
            return redirect('messaging:conversation', conv_pk=conv.pk)

    autre = conv.autre_participant(request.user)

    return render(request, 'messaging/conversation.html', {
        'conv':  conv,
        'msgs':  msgs,
        'autre': autre,
    })


@login_required
def demarrer_conversation(request, user_pk, article_pk=None):
    autre = get_object_or_404(User, pk=user_pk)
    if autre == request.user:
        return redirect('marketplace:liste')

    article = get_object_or_404(Article, pk=article_pk) if article_pk else None
    conv = Conversation.get_or_create_between(request.user, autre, article)
    return redirect('messaging:conversation', conv_pk=conv.pk)
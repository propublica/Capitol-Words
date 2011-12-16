


from django.shortcuts import render_to_response, redirect

CARD_LIST = [
    {   
        'slug': 'burgess',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Burgess%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Burgess%20-%20Audio.mp3',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-sledding',
        'share_text': "It's going to be tough sledding in the Senate. #CongressSez http://snlg.ht/urKxui via @sunfoundation",
    }, {
        'slug': 'collins1',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Collins1%20-%20Image.jpg',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-tree',
        'share_text': "This huge Christmas tree can hide a multitude of errors and policy surprises. #CongressSez http://snlg.ht/rzkYVz via @sunfoundation",
    }, {
        'slug': 'collins2',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Collins2%20-%20Image.jpg',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-benefits',
        'share_text': "Jingle all the way? #CongressSez http://snlg.ht/s1vf6B via @sunfoundation",
    }, {
        'slug': 'schultz',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Wasserman%20Schultz%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Wasserman%20Schultz%20-%20Audio.mp3',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-hanukkah',
        'share_text': "",
    }, {
        'slug': 'defazio1',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/DeFazio1%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/DeFazio1%20-%20Audio.mp3',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-april-fools',
        'share_text': "Ho, ho, ho, happy April Fools Day. #CongressSez http://snlg.ht/volr5D via @sunfoundation",
    }, {
        'slug': 'dorgan',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Dorgan%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Dorgan%20-%20Audio.mp3',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-april-fools',
        'share_text': "I've been poisoned! #CongressSez http://snlg.ht/ul2AEs via @sunfoundation",
    }, {
        'slug': 'english',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/English%20-%20Image.jpg',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-reindeer',
        'share_text': "No American is fooled by these reindeer games. #CongressSez http://snlg.ht/tDDBX4 via @sunfoundation",
    }, {
        'slug': 'mcdermott',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/McDermott%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/McDermott%20-%20Audio.mp3',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-darkness',
        'share_text': "Whether they read the one about the reindeer or the one about the baby Jesus... #CongressSez http://snlg.ht/u3PNfD via @sunfoundation",
    }, {
        'slug': 'smith',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Smith%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Smith%20-%20Audio.mp3',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-elves',
        'share_text': "Elves are not producing this money! #CongressSez http://snlg.ht/tPV7F6 via @sunfoundation",
    }, {
        'slug': 'defazio2',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/DeFazio2%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/DeFazio2%20-%20Audio.mp3',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-benefits',
        'share_text': "St. Nick is still alive, thank God. Alive, and in the Bahamas drinking champagne. #CongressSez http://snlg.ht/v9tWuh via @sunfoundation",
    }, {
        'slug': 'kennedy',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Kennedy%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Kennedy%20-%20Audio.mp3',
        'email_url': 'http://organizing.sunlightfoundation.com/page/share/capitol-greetings-yoda',
        'share_text': "Fear leads to anger; anger leads to hate; hate leads to suffering... #CongressSez http://snlg.ht/tiQXuy via @sunfoundation",
    }
]

CARDS = dict([(c['slug'], c) for c in CARD_LIST])


def all_cards(request):
    return render_to_response('cwod/christmas.html', {'cards': CARD_LIST})
    

def single_card(request, card_slug):
    if card_slug in CARDS:
        return render_to_response('cwod/christmas_card.html', {'card': CARDS[card_slug]})
    else:
        return redirect('cwod_christmas_card')
        
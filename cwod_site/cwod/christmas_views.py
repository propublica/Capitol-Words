


from django.shortcuts import render_to_response, redirect

CARD_LIST = [
    {   
        'slug': 'burgess',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Burgess%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Burgess%20-%20Audio.mp3'
    }, {
        'slug': 'collins1',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Collins1%20-%20Image.jpg'
    }, {
        'slug': 'collins2',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Collins2%20-%20Image.jpg'
    }, {
        'slug': 'defazio1',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/DeFazio1%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/DeFazio1%20-%20Audio.mp3',
    }, {
        'slug': 'dorgan',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Dorgan%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Dorgan%20-%20Audio.mp3',
    }, {
        'slug': 'english',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/English%20-%20Image.jpg',
    }, {
        'slug': 'mcdermott',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/McDermott%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/McDermott%20-%20Audio.mp3'
    }, {
        'slug': 'smith',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Smith%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Smith%20-%20Audio.mp3'
    }, {
        'slug': 'defazio2',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/DeFazio2%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/DeFazio2%20-%20Audio.mp3',
    }, {
        'slug': 'kennedy',
        'image_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Kennedy%20-%20Image.jpg',
        'audio_url': 'http://assets.sunlightfoundation.com.s3.amazonaws.com/files/capitolwords/christmas-2011/Kennedy%20-%20Audio.mp3',
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
        
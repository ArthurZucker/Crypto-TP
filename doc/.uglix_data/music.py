import threading

class GlobalVLCState:
    """no doc for you."""
    vlc = None
    instance = None
    player = None
    playing = None
    lock = None
    id = None
    enabled = False
    cache = {}

    def __init__(self, proto):
        self.lock = threading.Lock()
        try:
            self.proto = proto
            self.vlc = proto._uglix.uglix_import('vlc', 'vlc.py', '6085ed379e914309e75a73ea4949c0471cee638f97ed33e08368be2f3cb3e07b')
            self.vlc.logger.setLevel(4)
            i = self.vlc.Instance('--quiet')
            i.release()
            self.playing = None
            self.enabled = True
        except Exception as e:
            print()
            print('---------------------------------------------------------------------')
            print("Il semblerait que VLC ne soit pas installé ou ne soit pas fonctionnel.")
            print("Par conséquent, vous ne pouvez pas bénéficier de la bande son du TP.")
            print("Elle n'est pas indispensable pour faire le TP, mais ça le rend sûrement plus sympa.")
            print("Si vous êtes sous Linux, il suffit certainement d'utiliser votre gestionnaire de paquets")
            print("pour installer VLC. Sous Debian/Ubuntu : sudo apt-get install vlc.")
            print("Sous Windows/Mac OS X : installez VLC depuis le site web officiel.")
            print()
            print('reason : {}'.format(e))
            print('---------------------------------------------------------------------')
            print()
    
    def _clean(self):
        try:
            self.media.release()
            self.media = None
        except:
            pass
        try:
            self.player.release()
            self.player = None
        except:
            pass
        try:
            self.instance.release()
            self.instance = None
        except:
            pass
    
    def _stop(self):
        """
        must be called under the lock
        """
        try:
            self.player.stop()
        except:
            pass
        self.playing = None
        self._clean()        

    def stop(self):
        with self.lock:
            self._stop()

    def _play(self, uri, loop):
        """
        Play URI. Blocks until the song is over or the player is stopped.
        """
        assert self.instance is None
        self.proto._uglix.ensure_file('music/' + uri, uri, static=True)
        e = threading.Event()
        def SongFinished(event):
            """
            Callback for VLC's event manager.
            """
            e.set()
        options = ['--quiet']
        if loop:
            options.append('--input-repeat=9999')
        self.instance = self.vlc.Instance(options)
        self.player = self.instance.media_player_new()
        self.event_manager = self.player.event_manager()
        self.media = self.instance.media_new(self.proto._uglix.local_path(uri))
        self.player.set_media(self.media)
        self.event_manager.event_attach(self.vlc.EventType.MediaPlayerEndReached, SongFinished)
        self.player.play()
        e.wait()
        self.event_manager.event_detach(self.vlc.EventType.MediaPlayerEndReached)

    def play(self, uri, loop=False):
        """
        Play [uri] in the background. Return immediately.
        """
        with self.lock:
            if self.playing == uri:
                return
            if self.playing:
                self._stop()  # TODO : fadeout
            self.playing = uri
            threading.Thread(target=self._play, args=[uri, loop], daemon=True).start()

    def _play_list(self, uris, loop=False):
        i = 0
        while True:
            if self.playing != uris:
                break
            self._play(uris[i], loop=False)
            self._clean()
            i = (i + 1) % len(uris)
            if not loop:
                break

    def play_list(self, uris, loop=False):
        """
        Play [uris] in the background. Return immediately.
        """
        with self.lock:
            if self.playing == uris:
                return
            if self.playing:
                self._stop()  # TODO : fadeout
            self.playing = uris
            threading.Thread(target=self._play_list, args=[uris, loop], daemon=True).start()



    def sfx(self, uri):
        """
        Play a sound effect on top of the music.
        """
        threading.Thread(target=self._sfx, args=[uri], daemon=True).start()

    def _sfx(self, uri):
        self.proto._uglix.ensure_file('sfx/' + uri, uri, static=True)

        i = self.vlc.Instance()
        m = i.media_new(self.proto._uglix.local_path(uri))
        p = i.media_player_new()
        p.set_media(m)
        e = threading.Event()
        def SongFinished(event):
            e.set()
        em = p.event_manager()
        em.event_attach(self.vlc.EventType.MediaPlayerEndReached, SongFinished)
        p.play()
        e.wait()
        em.event_detach(self.vlc.EventType.MediaPlayerEndReached)
        p.release()
        m.release()
        i.release()
import logging


class EtapeAnimation:

    def __init__(self, duration, update=None):
        self.duration = max(float(duration), 0.001)
        self.update = update
        self.elapsed = 0.0


class SuiteAnimations:

    def __init__(self, on_finish, on_error):
        self.on_finish = on_finish
        self.on_error = on_error
        self.sequence = None
        self.current = None

    @property
    def busy(self):
        return self.sequence is not None

    def start(self, sequence):
        if self.busy:
            raise RuntimeError("Une animation est déjà en cours.")
        self.sequence = iter(sequence)
        self.current = None

    def cancel(self):
        close = getattr(self.sequence, "close", None)
        if close is not None:
            close()
        self.sequence = None
        self.current = None

    def update(self, delta):
        if not self.busy:
            return
        remaining = max(0.0, delta)
        try:
            while self.busy:
                if self.current is None:
                    try:
                        self.current = next(self.sequence)
                    except StopIteration:
                        self.sequence = None
                        self.on_finish()
                        return
                    if not isinstance(self.current, EtapeAnimation):
                        raise TypeError("Une étape d'animation n'est pas valide.")
                    if self.current.update is not None:
                        self.current.update(0.0)
                step = min(remaining, self.current.duration - self.current.elapsed)
                self.current.elapsed += step
                remaining -= step
                progress = min(1.0, self.current.elapsed / self.current.duration)
                if self.current.update is not None:
                    self.current.update(progress)
                if progress >= 1.0:
                    self.current = None
                    if remaining > 0:
                        continue
                return
        except Exception as error:
            logging.getLogger(__name__).exception("Échec de la séquence d'animation")
            self.cancel()
            self.on_error(error)

class Session:
    def __init__(self, session_id, last_buffer):
        self.session_id = session_id
        self.last_buffer = last_buffer

    def send_deltas(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diff = diff(self.last_buffer, new_buffer)
        # TODO: insert code to actually send deltas here.
        self.last_buffer = new_buffer

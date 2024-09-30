from peewee import *

from models.base_model import BaseModel


class Job(BaseModel):
    owner_id = TextField()

    command_args_j = TextField()

    priority = IntegerField()

    # Q = queued
    # R = running
    # P = paused
    state = TextField(constraints=[Check("state IN ('Q', 'R', 'P')")])

    last_seen_progress = IntegerField()
    last_restore_point = IntegerField()
    last_mask_len = IntegerField()
    last_maskfile_ind = IntegerField()
    max_progress = IntegerField()
    max_maskfile_ind = IntegerField()

    @staticmethod
    def get_running():
        return Job.get_or_none(Job.state == "R")

    @staticmethod
    def get_first_in_queue():
        return Job.select().order_by(Job.priority.desc()).get_or_none()

    def get_hashes(self):
        return [h.hash for h in self.hashes]  # type: ignore

    def get_results(self):
        return [h.result for h in self.get_hashes() if h.result is not None]

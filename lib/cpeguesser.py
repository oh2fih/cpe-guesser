#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import valkey
from dynaconf import Dynaconf

# Configuration
settings = Dynaconf(settings_files=["../config/settings.yaml"])
valkey_host = settings.get("valkey.host", "127.0.0.1")
valkey_port = settings.get("valkey.port", 6379)
valkey_db = settings.get("valkey.db", 8)


class CPEGuesser:
    VALID_CPE_PARTS = {"a", "h", "o"}

    def __init__(self, rdb=None):
        self.rdb = rdb or valkey.Valkey(
            host=valkey_host,
            port=valkey_port,
            db=valkey_db,
            decode_responses=True,
        )

    def _word_score(self, word, cpe):
        score = self.rdb.zscore(f"s:{word}", cpe)
        return score or 0

    def _rank_score(self, cpe):
        score = self.rdb.zscore("rank:cpe", cpe)
        return score or 0

    def _is_matching_part(self, cpe, part):
        if part is None:
            return True
        fields = cpe.split(":")
        if len(fields) < 3:
            return False
        return fields[2] == part

    def guessCpe(self, words, part=None):
        if part is not None:
            part = part.lower()
            if part not in self.VALID_CPE_PARTS:
                return []

        k = []
        for keyword in words:
            k.append(f"w:{keyword.lower()}")

        if not k:
            return []

        result = self.rdb.sinter(*k)
        if not result:
            return []

        ranked = []
        lowered_words = [word.lower() for word in words]

        for cpe in result:
            if not self._is_matching_part(cpe, part):
                continue
            search_score = sum(self._word_score(word, cpe) for word in lowered_words)
            rank_score = self._rank_score(cpe)
            total_score = search_score + rank_score
            ranked.append((total_score, rank_score, cpe))

        return [
            (total_score, cpe) for total_score, _, cpe in sorted(ranked, reverse=True)
        ]

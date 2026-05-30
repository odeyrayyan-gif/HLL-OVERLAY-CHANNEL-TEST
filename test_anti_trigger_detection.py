import unittest

import DO_NOT_EDIT_server as server


class AntiTriggerDetectionTests(unittest.TestCase):
    def test_synthetic_sample_flags_high_priority_candidate(self):
        report = server.build_anti_trigger_report(
            server.ANTI_TRIGGER_SAMPLE_STATS,
            list(server.ANTI_TRIGGER_SAMPLE_EVENTS),
            source="unit_test",
        )

        self.assertTrue(report["ok"])
        self.assertGreaterEqual(len(report["candidates"]), 1)
        top = report["candidates"][0]
        self.assertEqual(top["player"], "SyntheticSnap")
        self.assertGreaterEqual(top["score"], 70)
        self.assertEqual(top["recommendation"], "manual_review_high_priority")
        self.assertIn("crosshair position", report["summary"]["limitation"])

    def test_spaced_normal_kills_do_not_create_high_priority_signal(self):
        events = [
            {"timestamp": 1000, "killer": "Normal", "victim": "A", "weapon": "Rifle"},
            {"timestamp": 1040, "killer": "Normal", "victim": "B", "weapon": "Rifle"},
            {"timestamp": 1110, "killer": "Normal", "victim": "C", "weapon": "Grenade"},
            {"timestamp": 1180, "killer": "Normal", "victim": "D", "weapon": "SMG"},
        ]
        report = server.build_anti_trigger_report({}, events, source="unit_test")

        candidate = next((item for item in report["candidates"] if item["player"] == "Normal"), None)
        self.assertIsNone(candidate)

    def test_extracts_common_kill_log_shapes(self):
        payload = {
            "result": {
                "logs": [
                    {"type": "KILL", "time": "2026-05-27T04:58:00Z", "killer": "One", "victim": "Two", "weapon": "Rifle"},
                    {"message": "Three killed Four with SMG", "timestamp": 2000},
                    "Five killed Six with Pistol",
                ]
            }
        }

        events = server.extract_kill_events(payload)

        self.assertEqual(len(events), 3)
        by_killer = {event["killer"]: event for event in events}
        self.assertIn("One", by_killer)
        self.assertEqual(by_killer["Three"]["weapon"], "SMG")
        self.assertEqual(by_killer["Five"]["victim"], "Six")

    def test_stats_only_signal_is_low_confidence(self):
        stats = {
            "result": {
                "stats": [
                    {"player": "StatsOnly", "kills": 45, "deaths": 2, "weapons": {"Rifle": 43, "Grenade": 2}}
                ]
            }
        }
        report = server.build_anti_trigger_report(stats, [], source="unit_test")

        candidate = report["candidates"][0]
        self.assertEqual(candidate["player"], "StatsOnly")
        self.assertEqual(candidate["confidence"], "low")
        self.assertEqual(candidate["recommendation"], "watchlist")

    def test_windows_client_disconnects_are_treated_as_normal(self):
        err = ConnectionAbortedError("connection aborted")
        err.winerror = 10053

        self.assertTrue(server.is_client_disconnect_error(err))
        self.assertTrue(server.is_client_disconnect_error(BrokenPipeError()))
        self.assertFalse(server.is_client_disconnect_error(OSError("disk failed")))


if __name__ == "__main__":
    unittest.main()

from inmanta import const

def test_dryrun(project):
    project.compile("""
    import unittest

    unittest::Resource(name="res", desired_value="x")
    """)
    project.dryrun_resource("unittest::Resource", status=const.ResourceState.dry)


def test_dryrun_fail_skip(project):
    project.compile("""
    import unittest

    unittest::Resource(name="res", desired_value="x", fail=true)
    """)
    project.dryrun_resource("unittest::Resource", status=const.ResourceState.failed)

    project.compile("""
        import unittest

        unittest::Resource(name="res", desired_value="x", skip=true)
        """)
    project.dryrun_resource("unittest::Resource", status=const.ResourceState.skipped)
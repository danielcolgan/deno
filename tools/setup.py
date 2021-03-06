#!/usr/bin/env python
import third_party
from util import run, build_path, build_mode
import os
import sys
import distutils.spawn

third_party.fix_symlinks()
third_party.download_gn()
third_party.download_clang_format()
third_party.download_clang()
third_party.maybe_download_sysroot()


def get_gn_args():
    out = []
    if build_mode() == "release":
        out += ["is_official_build=true"]
    elif build_mode() == "debug":
        pass
    else:
        print "Bad mode {}. Use 'release' or 'debug' (default)" % build_mode()
        sys.exit(1)
    if "DENO_BUILD_ARGS" in os.environ:
        out += os.environ["DENO_BUILD_ARGS"].split()

    # Check if ccache is in the path, and if so we cc_wrapper.
    ccache_path = distutils.spawn.find_executable("ccache")
    if ccache_path:
        out += [r'cc_wrapper="%s"' % ccache_path]

    print "DENO_BUILD_ARGS:", out

    return out


# gn gen.
def gn_gen(mode):
    os.environ["DENO_BUILD_MODE"] = mode

    gn_args = get_gn_args()

    # mkdir $build_path(). We do this so we can write args.gn before running gn gen.
    if not os.path.isdir(build_path()):
        os.makedirs(build_path())

    # Rather than using gn gen --args we manually write the args.gn override file.
    # This is to avoid quoting/escaping complications when passing overrides as
    # command-line arguments.
    args_filename = os.path.join(build_path(), "args.gn")
    if not os.path.exists(args_filename) or gn_args:
        with open(args_filename, "w+") as f:
            f.write("\n".join(gn_args) + "\n")

    run([third_party.gn_path, "gen", build_path()],
        env=third_party.google_env())


mode = build_mode(default=None)
if mode is not None:
    gn_gen(mode)
else:
    gn_gen("release")
    gn_gen("debug")

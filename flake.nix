# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      #       ↑ Swap it for your system if needed
      #       "aarch64-linux" / "x86_64-darwin" / "aarch64-darwin"
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {

        packages = [
          pkgs.python310
          pkgs.poetry
        ];

        env = {
          # Workaround in linux: python downloads ELF's that can't find glibc
          # You would see errors like: error while loading shared libraries: name.so: cannot open shared object file: No such file or directory
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc
            pkgs.zlib
            # Add any missing library needed
            # You can use the nix-index package to locate them, e.g. nix-locate -w --top-level --at-root /lib/libudev.so.1
          ];

          # Put the venv on the repo, so direnv can access it
          POETRY_VIRTUALENVS_IN_PROJECT = "true";
          POETRY_VIRTUALENVS_PATH = "{project-dir}/.venv";

          # Use python from path, so you can use a different version to the one bundled with poetry
          POETRY_VIRTUALENVS_PREFER_ACTIVE_PYTHON = "true";
        };

        shellHook = ''
          echo Welcome to ekeko dev
        '';

      };
    };
}

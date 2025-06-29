# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-25.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # pkgs.go
    # pkgs.python311
    # pkgs.python311Packages.pip
    # pkgs.nodejs_20
    # pkgs.nodePackages.nodemon
    pkgs.fish
    pkgs.nodejs_latest
    pkgs.astro-language-server
    pkgs.pnpm
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
      "astro-build.astro-vscode"
    ];

    # Enable previews
    previews = {
      enable = false;
      previews = {
         web = {
        #   # Example: run "pnpm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
           command = ["pnpm" "run" "dev" "--" "--port" "8080"];
           manager = "web";
           env = {
        #     # Environment variables to set for your server
             PORT = "8080";
           };
         };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Example: install JS dependencies from NPM
        # npm-install = "pnpm install";
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # watch-backend = "pnpm run watch-backend";
      };
    };
  };
}

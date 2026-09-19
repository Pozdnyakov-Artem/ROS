FROM althack/ros2:jazzy-gazebo

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential pciutils mesa-utils vulkan-tools fish \
    && rm -rf /var/lib/apt/lists/*

ENV UV_INSTALL_DIR=/usr/local/bin \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_TOOL_DIR=/opt/uv-tools

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv tool install ruff \
    && uv tool install ty

USER ros

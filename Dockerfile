# Dashboard and allocator. Full Meridian MCMC stays a conda/CPU job.
# environment.yml names the env mmt-mmm, which conflicts with `-n base`.
FROM mambaorg/micromamba:2.3.1

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba create -y -f /tmp/environment.yml && \
    micromamba clean --all --yes && \
    rm -f /tmp/environment.yml

ENV ENV_NAME=mmt-mmm
ARG MAMBA_DOCKERFILE_ACTIVATE=1

WORKDIR /opt/mmt-mmm
COPY --chown=$MAMBA_USER:$MAMBA_USER . /opt/mmt-mmm

EXPOSE 8501
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]

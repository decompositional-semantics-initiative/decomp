FROM quay.io/jupyter/datascience-notebook:2024-11-19


# set working directory
WORKDIR "${HOME}/decomp"

# copy the package files
COPY --chown=${NB_UID}:${NB_GID} . .

# install the package and its dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e . && \
    # pre-build the UDS corpus to cache it in the image
    python -c "from decomp import UDSCorpus; UDSCorpus()"

# set the default command to start Jupyter Lab
CMD ["start-notebook.py", "--IdentityProvider.token=''", "--IdentityProvider.password=''"]
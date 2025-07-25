from datetime import datetime
import json
import os
import requests

def coll_info(base_url, repository_id, session_key, unique_resource_id, resource_ids_counter, resource_ids_to_audio_or_moving_image, resource_ids_to_number_audio_and_number_moving_image):
    
    print('  - GETting resource ' + str(unique_resource_id))
    endpoint = '/repositories/' + str(repository_id) + '/resources/' + str(unique_resource_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.get(base_url + endpoint, headers=headers)
    print(response)
    
    resource = response.json()
    '''
    with open(os.path.join('cache', 'resources', unique_resource_id + '.json'), mode='w') as f:
        json.dump(resource, f)'''
    
    print('\n- Appending extent')

    extents = resource['extents']
    for extent in extents:
        extent['portion'] = 'part'
    
    number_audio = [resource_id_to_number_audio_and_number_moving_image['audio'] for resource_id_to_number_audio_and_number_moving_image in resource_ids_to_number_audio_and_number_moving_image if resource_id_to_number_audio_and_number_moving_image['resource_id'] == unique_resource_id][0]
    number_moving_image = [resource_id_to_number_audio_and_number_moving_image['moving_image'] for resource_id_to_number_audio_and_number_moving_image in resource_ids_to_number_audio_and_number_moving_image if resource_id_to_number_audio_and_number_moving_image['resource_id'] == unique_resource_id][0]
    
    if number_audio > 0:
        extents.append(
            {
                'portion': 'part',
                'number': str(number_audio),
                'extent_type': 'digital audio files'
            }
        )
    if number_moving_image > 0:
        extents.append(
            {
                'portion': 'part',
                'number': str(number_moving_image),
                'extent_type': 'digital video files'
            }
        )

    
    print('\n- Appending "Processing Information" note')
    
    resource['notes'].append(
        {
            'jsonmodel_type': 'note_multipart',
            'type': 'processinfo',
            'publish': True,
            'subnotes': [{
                'jsonmodel_type': 'note_text',
                'content': 'In preparing digital material for long-term preservation and access, the Bentley Historical Library adheres to professional best practices and standards to ensure that content will retain its authenticity and integrity. For more information on procedures for the ingest and processing of digital materials, please see <title href="http://deepblue.lib.umich.edu/handle/2027.42/93344" show="new" actuate="onrequest">Bentley Historical Library Digital Processing Note</title>. Access to digital material may be provided either as a direct link to an individual file or as a downloadable package of files bundled in a zip file.',
            }],
        }
    )
    
    print('\n- Appending revision statements')
    
    resource['revision_statements'].append(
        {
            'date': str(datetime.now().date()),
            'description': 'Revised Extent Note, Processing Information Note and Existence and Location of Copies Note; added links to digitized content; added Conditions Governing notes for digitized content.',
            'jsonmodel_type': 'revision_statement',
            'publish': False
        }
    )        
    
    audio = [resource_id_to_audio_or_moving_image['audio'] for resource_id_to_audio_or_moving_image in resource_ids_to_audio_or_moving_image if resource_id_to_audio_or_moving_image['resource_id'] == unique_resource_id][0]
    moving_image = [resource_id_to_audio_or_moving_image['moving_image'] for resource_id_to_audio_or_moving_image in resource_ids_to_audio_or_moving_image if resource_id_to_audio_or_moving_image['resource_id'] == unique_resource_id][0]
    if audio == True:
        resource['revision_statements'].append(
            {
                'date': str(datetime.now().date()),
                'description': 'Added sound recording genre.',
                'jsonmodel_type': 'revision_statement',
                'publish': False
            }
        )
    if moving_image == True:
        resource['revision_statements'].append(
            {
                'date': str(datetime.now().date()),
                'description': 'Added video recording genre.',
                'jsonmodel_type': 'revision_statement',
                'publish': False
            }
        )
    
    print('\n- Appending "Existence and Locations of Copies" notes')
    
    resource['notes'].append(
        {
            'jsonmodel_type': 'note_multipart',
            'type': 'altformavail',
            'publish': True,
            'subnotes': [{
                'jsonmodel_type': 'note_text',
                'content': 'Digitization: A number of recordings within this collection have been digitized. The resulting files are available for playback online or in the Bentley Library Reading Room according to rights. Original media are only available for staff use.',
            }],
        }
    )

    print('\n- Appending "Conditions Governing Access" note')

    resource['notes'].append(
        {
            'jsonmodel_type': 'note_multipart',
            'type': 'accessrestrict',
            'publish': True,
            'subnotes': [{
                'jsonmodel_type': 'note_text',
                'content': 'Select recordings within this collection have been digitized. Original sound recordings are only available for staff use.'
            }]
        }
    )
    
    print('\n- Appending Genre / Form')
    
    audio = [resource_id_to_audio_or_moving_image['audio'] for resource_id_to_audio_or_moving_image in resource_ids_to_audio_or_moving_image if resource_id_to_audio_or_moving_image['resource_id'] == unique_resource_id][0]
    moving_image = [resource_id_to_audio_or_moving_image['moving_image'] for resource_id_to_audio_or_moving_image in resource_ids_to_audio_or_moving_image if resource_id_to_audio_or_moving_image['resource_id'] == unique_resource_id][0]
    
    # {'ref': '/subjects/3144'} is "sound recordings" from AAT
    if audio == True:
        if "/subjects/3144" not in [subject['ref'] for subject in resource['subjects']]:
            resource['subjects'].append({'ref': '/subjects/3144'})
    
    # {'ref': '/subjects/3208'} is "video recordings" from AAT
    if moving_image == True:
        if "/subjects/3208" not in [subject['ref'] for subject in resource['subjects']]:
            resource['subjects'].append({'ref': '/subjects/3208'})
            
    # {'ref': '/subjects/3191'} is "digital file formats" from AAT
    if "/subjects/3191" not in [subject['ref'] for subject in resource['subjects']]:
        resource['subjects'].append({'ref': '/subjects/3191'})
    
    print('  - POSTing resource ' + str(unique_resource_id))
    endpoint = '/repositories/' + str(repository_id) + '/resources/' + str(unique_resource_id)
    headers = {'X-ArchivesSpace-Session': session_key}
    response = requests.post(base_url + endpoint, headers=headers, data=json.dumps(resource))
    print(response.text)
    
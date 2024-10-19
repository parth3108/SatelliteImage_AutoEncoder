<script lang="js">
	import API from '$lib/internal/api';
	import * as Table from '$lib/components/ui/table/index.js';
	import { onMount } from 'svelte';
	import ViewImage from '$lib/internal/components/view-image.svelte';

	let folders = [];
	let files = [];
	let selectedFolder = '';
	let selectedFolderPath = '';

	onMount(async () => {
		const response = await API.listDirectories();
		folders = response.data;
	});
</script>

<div class="flex h-full flex-col">
	<span class="flex min-h-14 items-center justify-between border-b pl-4 pr-8"> View Dataset </span>

	<div class="m-4 rounded-lg border">
		<Table.Root>
			<Table.Header>
				<Table.Row>
					<Table.Head>Foler Name</Table.Head>
					<Table.Head>Folder Path</Table.Head>
					<Table.Head class="text-right">Files</Table.Head>
				</Table.Row>
			</Table.Header>
			<Table.Body>
				{#each folders as folder, i (i)}
					<Table.Row>
						<Table.Cell class="font-medium">{folder.name}</Table.Cell>
						<Table.Cell
							>{folder.path.replace(
								'/Users/yashpulse/Library/CloudStorage/OneDrive-SwinburneUniversity/Semester 4/TAP/CH1/api/',
								''
							)}</Table.Cell
						>
						<Table.Cell
							class="cursor-pointer text-right text-[#e11d48] hover:underline"
							on:click={() => {
								files = folder.files;
								selectedFolder = folder.name;
								selectedFolderPath = folder.path;
							}}>{folder?.files?.length ?? 0}</Table.Cell
						>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
	{#if files.length > 0}
		<span class="flex min-h-14 items-center justify-between border-b border-t pl-4 pr-8">
			Files: {selectedFolder}
		</span>
		<div class="m-4 max-h-full flex-grow overflow-auto rounded-lg border">
			<Table.Root>
				<Table.Header>
					<Table.Row>
						<Table.Head>File Name</Table.Head>
						<Table.Head class="text-right">Extension</Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each files as file, i (i)}
						<Table.Row>
							<Table.Cell class="font-medium">
								<ViewImage
									name={file.replace(
										'/Users/yashpulse/Library/CloudStorage/OneDrive-SwinburneUniversity/Semester 4/TAP/CH1/api/',
										''
									)}
									path={selectedFolderPath + '/' + file}
								></ViewImage></Table.Cell
							>
							<Table.Cell class="cursor-pointer text-right hover:text-[#e11d48] hover:underline"
								>{file?.split('.')[file?.split('.').length - 1]}</Table.Cell
							>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{/if}
</div>

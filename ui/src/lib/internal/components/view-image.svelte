<script lang="js">
	import { Button, buttonVariants } from '$lib/components/ui/button/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import API from '../api';
	import { fly, fade } from 'svelte/transition';

	export let name = '';
	export let path = '';

	let base64Image = '';
	let isLoading = false;

	const getImageType = (base64String) => {
		const mime = base64String.substring(0, 4);
		switch (mime) {
			case '/9j/':
				return 'image/jpeg';
			case 'iVBOR':
				return 'image/png';
			case 'R0lG':
				return 'image/gif';
			case 'UklG':
				return 'image/webp';
			case 'SUkq':
			case 'II2A':
				return 'image/tiff';
			default:
				return 'image/png'; // Fallback to PNG
		}
	};

	const getImage = async () => {
		isLoading = true;
		base64Image = '';
		try {
			const response = await API.getImageByPath(path);

			if (response?.isSuccess) {
				const imageType = getImageType(response?.data);
				base64Image = `data:${imageType};base64,${response?.data}`;
			} else {
				base64Image = '';
			}
		} catch (error) {
			console.error(error);
		} finally {
			isLoading = false;
		}
	};
</script>

<Dialog.Root>
	<Dialog.Trigger class={buttonVariants({ variant: 'link' })}>{name}</Dialog.Trigger>
	<Dialog.Content class="min-h-[90vh] max-w-[720px]">
		<Dialog.Header>
			<Dialog.Title>Image</Dialog.Title>
			<Dialog.Description>
				{name}
			</Dialog.Description>
		</Dialog.Header>
		<div class="h-full w-full" on:click={getImage()}>
			{#if isLoading}
				<p>Loading ...</p>
			{:else if base64Image === ''}
				<p>No Image Found</p>
			{:else}
				<img src={base64Image} out:fly={{ y: 300, duration: 1000 }} in:fade={{ delay: 300 }} />
			{/if}
		</div>
	</Dialog.Content>
</Dialog.Root>

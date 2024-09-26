<script>
    import { getContext } from 'svelte';
    import { user } from '$lib/stores';

    const i18n = getContext('i18n');

    // Здесь должна быть логика получения информации о тарифе пользователя
    let userPlan = "Базовый"; // Пример
</script>

<div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-4">{$i18n.t('Your Plan')}</h1>
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-2">{userPlan}</h2>
        <!-- Здесь добавьте описание тарифа -->
        <p>Описание вашего текущего тарифа...</p>
        <ul class="mt-4 list-disc list-inside">
            <li>Функция 1</li>
            <li>Функция 2</li>
            <li>Функция 3</li>
        </ul>
    </div>
</div>
